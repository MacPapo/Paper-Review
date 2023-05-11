from datetime import datetime
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import PDF, Project, Version, Researcher
from app.auth.crypt import Crypt


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/")
@bp.route("/index")
@bp.route("/home")
def index():
    if current_user.is_authenticated:
        if current_user.type == "researcher":
            projects = current_user.projects
            versions = []
            for p in projects:
                versions.append(
                    p.versions[-1]
                )
            return render_template(
                "index.html", title="Home", projects=versions, researcher=True
            )
        elif current_user.type == "reviewer":
            projects = Project.query.all()
            return render_template("index.html", title="Home", projects=projects)
    return render_template("index.html", title="Home")


@bp.route("/about")
def about():
    return render_template("about.html", title="About")


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
