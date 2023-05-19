from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.blueprints.project import bp
from app.blueprints.project.forms import UploadForm
from app.models import Project, Version, Draft
from app.modules.pdf_helper import upload_pdf, get_pdf


@bp.route("/projects")
@login_required
def projects():
    if current_user.is_authenticated:
        if current_user.type == "reviewer":
            projects = Project.query.all()
            versions = [p.versions[-1] for p in projects]
            return render_template(
                "projects.html", title="All Projects", projects=versions
            )
        else:
            versions = [p.versions[-1] for p in current_user.projects]
            return render_template(
                "projects.html", title="Your Projects", projects=versions
            )
    else:
        return redirect(url_for("auth.login"))


@bp.route("/project/create", methods=["GET", "POST"])
@login_required  # this decorator will make sure that the user is logged in
def create():
    form = UploadForm()
    if form.validate_on_submit():
        pdfs = upload_pdf(form.pdfs.data)

        new_project = Project(researcher=current_user)
        db.session.add(new_project)
        db.session.commit()

        new_draft = Draft(
            title=form.title.data,
            description=form.description.data,
        )

        new_version = Version(
            version_number=1,
            project_title=form.title.data,
            project_description=form.description.data,
            project_status="Submitted",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            project=new_project,
            draft=new_draft,
        )

        new_draft.version = new_version

        db.session.add(new_version, new_draft)

        # Add the PDF objects to the draft and version
        new_draft.contains = pdfs
        new_version.contains = pdfs

        db.session.commit()

        flash("Congratulations, you have submitted a PDF!")
        return redirect(url_for("main.index"))

    return render_template(
        "projects_components/create_project.html", title="Upload", form=form
    )


@bp.route("/project/view/<int:pid>/<int:version_number>")
@login_required
def view(pid, version_number):
    project = Project.query.filter_by(pid=pid).first_or_404()

    if version_number > len(project.versions):
        return render_template("errors/404.html"), 404

    get_pdf_lambda = lambda x: get_pdf(x)

    return render_template(
        "view.html",
        title="View Project",
        project=project,
        version_number=version_number,
        get_pdf_lambda=get_pdf_lambda,
    )


@bp.route("/project/edit/<int:vid>")
@login_required
def edit(vid):
    form = UploadForm()
    form_pdf = UploadForm()

    draft = Version.query.filter_by(vid=vid).first_or_404().draft

    form.title.data = draft.title
    form.description.data = draft.description

    pdfs = get_pdf(draft.contains)

    return render_template(
        "projects_components/edit_project.html",
        title="View Project",
        counter=len(pdfs),
        pdfs=pdfs,
        form=form,
        form_pdf=form_pdf,
        vid=vid,
    )


@bp.route("/project/edit_draft/<int:vid>", methods=["POST"])
@login_required
def edit_draft(vid):
    if request.method == "POST":
        draft = Version.query.filter_by(vid=vid).first_or_404().draft

        draft.title = request.form.get("title")
        draft.description = request.form.get("description")
        names = request.form.getlist("names")

        pdfs = upload_pdf(request.files.getlist("files"))
        draft.contains = [pdf for pdf in draft.contains if pdf.filename in names] + pdfs

        db.session.commit()
        return ("", 204)


@bp.route("/project/update_version/<int:vid>", methods=["POST"])
@login_required
def update_version(vid):
    if request.method == "POST":
        version = Version.query.filter_by(vid=vid).first_or_404()
        draft = version.draft
        project = version.project

        new_draft = Draft(
            title=draft.title,
            description=draft.description,
            contains=[pdf for pdf in draft.contains],
        )

        new_version = Version(
            version_number=version.version_number + 1,
            project_title=draft.title,
            project_description=draft.description,
            project_status=version.project_status,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            project=project,
            draft=new_draft,
        )

        new_draft.version = new_version

        db.session.add(new_version, new_draft)
        db.session.commit()

        new_version.contains = [pdf for pdf in new_draft.contains]

        db.session.commit()
        return ("", 204)


@bp.route("/project/discard_draft/<int:vid>", methods=["POST"])
@login_required
def discard_draft(vid):
    if request.method == "POST":
        version = Version.query.filter_by(vid=vid).first_or_404()
        draft = version.draft

        draft.title = version.project_title
        draft.description = version.project_description

        draft.contains = [pdf for pdf in version.contains]

        db.session.commit()
        return ("", 204)
