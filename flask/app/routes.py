import os, tempfile
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse  # this is used to parse the url
from werkzeug.utils import secure_filename
from app import app, db, firebase
from app.modules.forms import UploadForm


# firebase = Firebase()
# # select a file and firebase upload it
# x = firebase.upload('Dockerfile')
# app.logger.info(x[0])
# app.logger.info(x[1])
# app.logger.info(firebase.decrypt(x[0], x[1]))


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        upload_file_location = os.path.join("uploads", filename)
        f.save(upload_file_location)
        x = firebase.upload(upload_file_location)
        os.remove(upload_file_location)
        return redirect(url_for("upload"))
    return render_template("upload.html", title="Upload", form=form)


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash("Invalid username or password")
#             return redirect(url_for("login"))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get("next")
#         if not next_page or url_parse(next_page).netloc != "":
#             next_page = url_for("index")
#         return redirect(next_page)
#     return render_template("login.html", title="Sign In", form=form)


# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("index"))


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash("Congratulations, you are now a registered user!")
#         return redirect(url_for("login"))
#     return render_template("register.html", title="Register", form=form)
