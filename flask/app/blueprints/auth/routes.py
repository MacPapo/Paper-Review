import os
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse  # this is used to parse the url
from app import db, firebase
from app.blueprints.auth import   bp
from app.modules.crypt import Crypt
from app.models import Researcher, Reviewer, PDF
from .forms import (
    LoginUserForm,
    RegistrationResearcherForm,
    RegistrationReviewerForm,
    EditUserForm,
)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginUserForm()
    if form.validate_on_submit():
        researcher = Researcher.query.filter_by(username=form.username.data).first()
        reviewer = Reviewer.query.filter_by(username=form.username.data).first()

        # Researcher and Reviewer are None if the username is not found
        if researcher is None and reviewer is None:
            current_app.logger.info(
                "Invalid username or password for user %s", form.username.data
            )
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        # Researcher exists and password is incorrect
        if researcher is not None and not researcher.check_password(form.password.data):
            current_app.logger.info(
                "Invalid username or password for user %s", form.username.data
            )
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        # Reviewer exists and password is incorrect
        if reviewer is not None and not reviewer.check_password(form.password.data):
            current_app.logger.info(
                "Invalid username or password for user %s", form.username.data
            )
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        # Researcher exists and password is correct
        if researcher is not None and researcher.check_password(form.password.data):
            login_user(researcher, remember=form.remember_me.data)
            flash("Welcome back, {}".format(researcher.fullname()))
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("main.index")
                return redirect(next_page)

        # Reviewer exists and password is correct
        if reviewer is not None and reviewer.check_password(form.password.data):
            login_user(reviewer, remember=form.remember_me.data)
            flash("Welcome back, {}".format(reviewer.fullname()))
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("main.index")
                return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register/researcher", methods=["GET", "POST"])
def register_researcher():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationResearcherForm()
    if form.validate_on_submit():
        researcher = Researcher(
            uid=form.uid.data.upper(),
            username=form.username.data,
            first_name=form.firstname.data,
            last_name=form.lastname.data,
            birthdate=form.birthdate.data,
            email=form.email.data,
            sex=form.sex.data,
            nationality=form.nationality.data,
            phone=form.phone.data,
            department=form.department.data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        researcher.set_password(form.password.data)

        db.session.add(researcher)
        db.session.commit()

        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("auth.login"))
    return render_template(
        "registration/register_researcher.html", title="Register", form=form
    )


@bp.route("/register/reviewer", methods=["GET", "POST"])
def register_reviewer():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationReviewerForm()
    if form.validate_on_submit():
        correct_file_name = lambda n: os.path.join(
            "uploads",
            Path(secure_filename(n)).stem
            + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S")
            + ".pdf",
        )

        filename = correct_file_name(form.pdf.data.filename)
        form.pdf.data.save(filename)

        cr = Crypt()
        pdf_cr = cr.encrypt_url(firebase.upload(filename))
        pdf = PDF(id=pdf_cr[0],filename=form.pdf.data.filename, key=pdf_cr[1])
        os.remove(filename)

        reviewer = Reviewer(
            uid=form.uid.data.upper(),
            username=form.username.data,
            first_name=form.firstname.data,
            last_name=form.lastname.data,
            birthdate=form.birthdate.data,
            email=form.email.data,
            sex=form.sex.data,
            nationality=form.nationality.data,
            department=form.department.data,
            phone=form.phone.data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pdf=pdf,
        )
        reviewer.set_password(form.password.data)

        db.session.add(pdf)
        db.session.add(reviewer)
        db.session.commit()

        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("auth.login"))
    return render_template(
        "registration/register_reviewer.html", title="Register", form=form
    )


@bp.route("/user/<username>")
@login_required
def profile(username):
    researcher = Researcher.query.filter_by(username=username).first()
    reviewer = Reviewer.query.filter_by(username=username).first()

    if researcher is None and reviewer is None:
        return render_template("errors/404.html"), 404

    if researcher is not None:
        latest_versions = []
        for project in researcher.projects:
            latest_versions.append(project.versions[-1])

        res = [0, 0, 0, 0]
        for version in latest_versions:
            if version.project_status == "Approved":
                res[0] += 1
            elif version.project_status == "Submitted":
                res[1] += 1
            elif version.project_status == "Requires changes":
                res[2] += 1
            elif version.project_status == "Rejected":
                res[3] += 1

        calc_percentage = lambda x, y: round((x / y) * 100) if y != 0 else 0

        return render_template(
            "profile.html",
            title="profile",
            user=researcher,
            approved=calc_percentage(res[0], len(latest_versions)),
            submitted=calc_percentage(res[1], len(latest_versions)),
            requires_changes=calc_percentage(res[2], len(latest_versions)),
            rejected=calc_percentage(res[3], len(latest_versions)),
        )
    else:
        return render_template(
            "profile.html",
            title="profile",
            user=reviewer,
            approved=0,
            submitted=0,
            requires_changes=0,
            rejected=0,
        )


@bp.route("/user/<username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    form = EditUserForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.birthdate = form.birthdate.data
        current_user.sex = form.sex.data
        current_user.nationality = form.nationality.data
        current_user.updated_at = datetime.now()
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("auth.profile", username=current_user.username))
    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.birthdate.data = current_user.birthdate
        form.sex.data = current_user.sex
        form.nationality.data = current_user.nationality
    return render_template("edit_profile.html", title="Edit Profile", form=form)
