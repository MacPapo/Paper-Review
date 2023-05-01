import os
from datetime import datetime
from pathlib import Path
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse  # this is used to parse the url
from werkzeug.utils import secure_filename
from app import app, db, firebase
from app.models import User, Researcher, PDF
from app.modules.crypt import Crypt
from app.modules.forms import LoginForm, RegistrationForm, UploadForm


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", title="Home")


@app.route("/about")
@login_required  # this decorator will make sure that the user is logged in
def about():
    return render_template("about.html", title="About")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #Non esiste utente con questo  username
        if user is None or not user.check_password(form.password.data):
            app.logger.info("Invalid username or password for user %s", form.username.data)
            flash("Invalid username or password")
            return redirect(url_for("login"))
        #Controllo se è un ricercatore o reviewer
        researcher = (
            User.query.join(Researcher, User.uid == Researcher.rsid)
            .filter_by(rsid=user.get_id())
            .first()
        )
        if researcher is None:
            app.logger.info("User %s is not a researcher", form.username.data)
            return redirect(url_for("login"))
        else:
            app.logger.info("User %s is a researcher", form.username.data)
            login_user(researcher, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("index")
                return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            uid=form.uid.data,
            username=form.username.data,
            first_name=form.firstname.data,
            last_name=form.lastname.data,
            birthdate=form.birthdate.data,
            email=form.email.data,
            sex=form.sex.data,
            nationality=form.nationality.data,
            phone=form.phone.data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.add(Researcher(rsid=user.uid))
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/upload", methods=["GET", "POST"])
@login_required  # this decorator will make sure that the user is logged in
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Description of the lambda function:
        # 1. secure_filename(n) returns a string of the filename with all the special characters removed.
        #    For example, if n = "hello world.pdf", then secure_filename(n) = "hello world.pdf"
        #
        # 2. Path(secure_filename(n)).stem returns the filename without the extension.
        #    For example, if n = "hello world.pdf", then Path(secure_filename(n)).stem = "hello world"
        #
        # 3. datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") returns the current date and time in the format of "-YYYY-MM-DD-HH:MM:SS"
        #    For example, if the current date and time is 2020-07-01 12:00:00, then datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") = "-2020-07-01-12:00:00"
        #
        # 4. Putting it all together, if n = "hello world.pdf", then correct_file_name(n) = "uploads/hello world-2020-07-01-12:00:00.pdf"
        #    If n = "hello world!.pdf", then correct_file_name(n) = "uploads/hello world!-2020-07-01-12:00:00.pdf"
        #
        # 5. os.path.join("uploads", Path(secure_filename(n)).stem + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") + ".pdf") returns the filename with the path.
        #    For example, if n = "hello world.pdf", then os.path.join("uploads", Path(secure_filename(n)).stem + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") + ".pdf") = "uploads/hello world-2020-07-01-12:00:00.pdf"
        correct_file_name = lambda n: os.path.join(
            "uploads",
            Path(secure_filename(n)).stem
            + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S")
            + ".pdf",
        )

        # Description of the following code:
        # 1. The user uploads some files.
        # 2. The files are saved to the server.
        files = []
        for f in form.pdfs.data:
            filename = correct_file_name(f.filename)
            f.save(filename)
            files.append(filename)

        # 3. The files are uploaded to Firebase.
        # 4. The Links that Firebase returns will be encrypted.
        crypt = Crypt()
        pdf_urls = []
        for filename in files:
            pdf_urls.append(crypt.encrypt_url(firebase.upload(filename)))

        # 5. The encrypted files's url is saved to the database.
        for pdf_url in pdf_urls:
            db.session.add(PDF(id=pdf_url[0], key=pdf_url[1]))

        # 6. The files are deleted from the server.
        for filename in files:
            os.remove(filename)

        # 7. The database is committed.
        db.session.commit()

        # 8. A message is flashed to the user.
        flash("Congratulations, you have submitted a PDF!")

        # 9. The user is redirected to the home page.
        redirect(url_for("index"))

    return render_template("upload.html", title="Upload", form=form)


@app.route("/pdfs")
@login_required  # this decorator will make sure that the user is logged in
def pdfs():
    pdfs_enc = PDF.query.all()
    if pdfs_enc:
        crypt = Crypt()
        pdfs = []
        for pdf in pdfs_enc:
            pdfs.append(crypt.decrypt(pdf.key, pdf.id))
        return render_template("pdfs.html", title="PDFs", pdfs=pdfs)
    return render_template("index.html", title="PDFs")


@app.route("/user/<username>")
@login_required
def profile(username):
    # TODO: add a check to see if the user is a researcher or a reviewer
    user = (
        User.query.join(Researcher, User.uid == Researcher.rsid)
        .filter(User.username == username)
        .first_or_404()
    )
    user_type = "Researcher"
    return render_template(
        "profile.html", title="profile", user=user, user_type=user_type
    )


@app.before_request
def before_request():
    if current_user.is_authenticated:
        this_user = current_user.get_this_user()
        this_user.last_seen = datetime.utcnow()
        db.session.commit()
