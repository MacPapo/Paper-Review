from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.project import bp, logger
from app.project.forms import UploadForm
from app.models import Project, Version, Draft, PDF
from app.modules.pdf_helper import upload_pdf, get_pdf


@bp.route("/projects")
@login_required
def projects():
    if current_user.is_authenticated:
        if current_user.type == "reviewer":
            projects = Project.query.all()
            versions = []
            for p in projects:
                versions.append(p.versions[-1])
            return render_template(
                "projects.html", title="All Projects", projects=versions
            )
        else:
            versions = []
            for p in current_user.projects:
                versions.append(p.versions[-1])
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

        # 5.1 Create a project object
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
        db.session.commit()

        # 5.2 cretate new PDFVersions objects
        for pdf in pdfs:
            new_draft.contains.append(pdf)
            new_version.contains.append(pdf)

        # 7. The database is committed.
        db.session.commit()

        # 8. A message is flashed to the user.
        flash("Congratulations, you have submitted a PDF!")
        return redirect(url_for("main.index"))

    return render_template(
        "projects_components/create_project.html", title="Upload", form=form
    )


@bp.route("/project/view/<int:vid>")
@login_required
def view(vid):
    version = Version.query.filter_by(vid=vid).first_or_404()
    pdfs = get_pdf(version.contains)

    return render_template(
        "view.html", title="View Project", version=version, pdfs=pdfs
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

        db.session.begin_nested()
        pdfs = upload_pdf(request.files.getlist("files"))
        for pdf in draft.contains:
            if pdf.filename not in names:
                draft.contains.remove(pdf)

        for pdf in pdfs:
            draft.contains.append(pdf)

        db.session.commit()
        return('', 204)

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
        )

        for pdf in draft.contains:
            new_draft.contains.append(pdf)

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

        for pdf in new_draft.contains:
            new_version.contains.append(pdf)

        db.session.commit()
        return('', 204)
