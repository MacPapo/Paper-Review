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
        this_user = current_user.get_this_user()
        this_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/")
@bp.route("/index")
@bp.route("/home")
def index():
    latest_versions = []
    if current_user.is_authenticated:
        projects = (
            Project.query.join(Researcher).filter_by(rsid=current_user.rsid).all()
        )
        for project in projects:
            latest_versions.append(
                Version.query.join(Project).filter_by(pid=project.pid).first()
            )
    return render_template(
        "index.html", title="Home", projects=latest_versions, len=len(latest_versions)
    )


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
