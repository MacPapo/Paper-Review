import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from app import db, firebase
from app.main import bp
from app.main.forms import UploadForm
from app.models import PDF
from app.auth.crypt import Crypt
from pathlib import Path
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        this_user = current_user.get_this_user()
        this_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/")
@bp.route("/index")
@bp.route("/home")
def index():
    return render_template("index.html", title="Home")


@bp.route("/about")
def about():
    return render_template("about.html", title="About")


@bp.route("/upload", methods=["GET", "POST"])
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
            current_app.logger.info("Deleting file: " + filename)
            os.remove(filename)

        # 7. The database is committed.
        db.session.commit()

        # 8. A message is flashed to the user.
        flash("Congratulations, you have submitted a PDF!")

        # 9. The user is redirected to the home page.
        redirect(url_for("main.index"))

    return render_template("upload.html", title="Upload", form=form)


@bp.route("/pdfs")
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
