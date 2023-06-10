from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.util.langhelpers import portable_instancemethod
from app import db
from app.blueprints.project import bp
from app.blueprints.project.forms import UploadForm, ReportForm
from app.models import Project, Version, Draft, Report, ReportDraft
from app.modules.pdf_helper import *
from sqlalchemy import desc

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


@bp.route("/reports")
@login_required
def reports():
    reports = Report.query.filter_by(rvid=current_user.uid).all()
    return render_template("reports.html", title="Your Reports", reports=reports)


@bp.route("/project/<int:pid>/version/<int:vid>/add_report/")
@login_required
def add_report(pid, vid):
    form = ReportForm()
    draft = ReportDraft.query.filter_by(pid=pid,rvid= current_user.uid).order_by(desc(ReportDraft.created_at)).first()
    reports = Report.query.filter_by(pid=pid).all()
    if draft and draft.reference != 0:
        report = Report.query.filter_by(rid=draft.reference).first()
        if report:
            form.report.choices = [(draft.reference,str(report.rid)+"-"+str(report.title))]+[(0,"Nothing")]+[(r.rid,str(r.rid) +"-"+str(r.title )) for r in reports if not r.rid == draft.reference]
        else:
            form.report.choices = [(0,"Select a Report to refer")]+[(r.rid,str(r.rid) +"-"+str(r.title )) for r in reports]
    else:
        form.report.choices = [(0,"Select a Report to refer")]+[(r.rid,str(r.rid) +"-"+str(r.title )) for r in reports]
    if not draft:
        new_draft = ReportDraft(
            title = "Title",
            body = "Body",
            rvid = current_user.uid,
            pid = pid,
            status = "Requires changes",
        )
        pdfs = Version.query.filter_by(vid=vid).order_by(Version.created_at.desc()).first_or_404().contains
        new_draft.contains = [pdf for pdf in pdfs]
        db.session.add(new_draft)
        db.session.commit()
        form.title.data = new_draft.title
        form.body.data = new_draft.body
        form.status.data = new_draft.status
    else:
        form.title.data = draft.title
        form.body.data = draft.body
        form.status.data = draft.status
        pdfs = [pdf for pdf in draft.contains]
    pdfs = get_all_pdfs(pdfs)
    return render_template(
        "edit_report.html", title="Add Report",
        counter=len(pdfs),
        form=form,
        pid=pid,
        vid=vid,
        pdfs=pdfs,
    )


@bp.route("/project/create", methods=["GET", "POST"])
@login_required  # this decorator will make sure that the user is logged in
def create():
    form = UploadForm()
    if form.validate_on_submit():
        pdfs = upload_pdf("uploads", form.pdfs.data)
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

    get_pdf_lambda = lambda x: get_all_pdfs(x)

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

    pdfs = get_all_pdfs(draft.contains)

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

        pdfs = upload_pdf("uploads", request.files.getlist("files"))
        draft.contains = [pdf for pdf in draft.contains if pdf.filename in names] + pdfs

        db.session.commit()
        pdfs = draft.contains
        delete_pdf(pdfs)
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

#############################################################################


@bp.route("/project/edit/<int:vid>/edit_pdf/<filename>", methods=["POST", "GET"])
@login_required
def edit_pdf(vid, filename):
    draft = Version.query.filter_by(vid=vid).first_or_404().draft
    name = filename + ".pdf"
    if request.method == "POST":
        pdfs = draft.contains
        delete_pdf(pdfs)
        pdf = request.files["pdf"]
        pdf_obj = upload_pdf("uploads", [pdf])
        draft.contains = [
            pdf for pdf in draft.contains if pdf.filename != name
        ] + pdf_obj
        db.session.commit()
        return ("", 204)

    if request.method == "GET":
        link = download_pdf(name)
        return render_template(
            "edit_pdf.html",
            title="PDF VIEW",
            vid=vid,
            link=link,
            filename=name
        )

@bp.route("/project/<int:pid>/edit_report_draft/<int:vid>", methods=["POST"])
@login_required                                                                                                               #
def edit_report_draft(pid,vid):                                                                                               #
    if request.method == "POST":                                                                                              #
        draft = ReportDraft.query.filter_by(pid=pid,rvid=current_user.uid).order_by(desc(ReportDraft.created_at)).first_or_404()                                                                                                                     #
        draft.title = request.form.get("title")
        draft.body = request.form.get("body")
        draft.status = request.form.get("status")
        if request.form.get("report") != None:
            draft.reference = request.form.get("report")
        else:
            draft.reference = 0
        names = request.form.getlist("names")                                                                                 #
                                                                                                                              #
        pdfs = upload_pdf("uploads", request.files.getlist("files"))                                                          #
        draft.contains = [pdf for pdf in draft.contains if pdf.filename in names] + pdfs                                #
        db.session.commit()                                                                                                   #
        pdfs = draft.contains                                                                                                 #
        delete_pdf(pdfs)
        return ("",204)                                                                                                       #

@bp.route("/project/<int:pid>/update_report/<int:vid>", methods=["POST"])
@login_required
def update_report(vid,pid):
    if request.method == "POST":
        draft = ReportDraft.query.filter_by(pid=pid,rvid=current_user.uid).first()
        version = Version.query.filter_by(vid=vid).order_by(desc(Version.version_number)).first()
        if draft.reference != 0:
            reference = draft.reference
        else:
            reference = None
        new_report = Report(
            title=draft.title,
            body=draft.body,
            rvid=draft.rvid,
            pid=pid,
            rdraft_id=draft.rdid,
            reference=reference,
            contains=[pdf for pdf in draft.contains],
            draft=draft,
        )
        version.project_status = draft.status
        new_report.rdraft_id = draft.rdid
        new_report.version = [version]
        new_report.draft = draft
        db.session.add(new_report)
        db.session.commit()

        if draft.status== "Requires changes":
            new_draft= ReportDraft(
                title = 'Title',
                body = 'Body',
                rvid = current_user.uid,
                pid = pid,
                status = "Requires changes",
            )
            db.session.add(new_draft)
            db.session.commit()
            new_draft.contains = [pdf for pdf in version.contains]
            db.session.commit()

        return ("", 204)


@bp.route("/project/<int:pid>/discard_report_draft/<int:vid>", methods=["POST"])
@login_required
def discard_report_draft(vid,pid):
    if request.method == "POST":
        draft = ReportDraft.query.filter_by(pid=pid,rvid=current_user.uid).first_or_404()
        version = Version.query.filter_by(vid=vid).order_by(desc(Version.version_number)).first()
        draft.title = 'Title'
        draft.body = 'Body'
        draft.reference = 0
        draft.status ="Requires changes"
        if len(version.contains) != 0:
            draft.contains = [pdf for pdf in version.contains]
        else:
            draft.contains = []
        db.session.commit()
        return ("", 204)
