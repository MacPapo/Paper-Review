import os
from urllib.parse import unquote
from datetime import datetime
from pathlib import Path
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db, firebase
from app.project import bp
from app.project.forms import UploadForm
from app.models import PDF, Project, Version, Researcher, PDFVersions
from app.auth.crypt import Crypt


@bp.route("/projects")
@login_required
def projects():
    latest_versions = []
    if current_user.is_authenticated:
        if current_user.type == "reviewer":
            return render_template("projects.html", title="Projects", projects=Project.query.all())
        else:
            return render_template("projects.html", title="Projects", user=current_user)
    else:
        return redirect(url_for("auth.login"))


@bp.route("/project/create", methods=["GET", "POST"])
@login_required  # this decorator will make sure that the user is logged in
def create():
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

        # 5.1 Create a project object
        new_project = Project(rsid=current_user.rsid)
        db.session.add(new_project)
        db.session.commit()

        new_version = Version(
            version_number=1,
            project_title=form.title.data,
            project_description=form.description.data,
            project_status="Submitted",
            pid=new_project.pid,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.session.add(new_version)
        db.session.commit()

        # 5.2 cretate new PDFVersions objects
        for pdf_url in pdf_urls:
            db.session.add(PDFVersions(id=pdf_url[0], vid=new_version.vid))

        # 6. The files are deleted from the server.
        for filename in files:
            os.remove(filename)

        # 7. The database is committed.
        db.session.commit()

        # 8. A message is flashed to the user.
        flash("Congratulations, you have submitted a PDF!")

        # 9. The user is redirected to the home page.
        redirect(url_for("main.index"))

    return render_template(
        "projects_components/create_project.html", title="Upload", form=form
    )


@bp.route("/project/view/<int:vid>")
@login_required
def view(vid):
    version = Version.query.filter_by(vid=vid).first_or_404()

    pdfs_raw = PDF.query.join(PDFVersions).filter_by(vid=vid).all()

    crypt = Crypt()
    pdfs = []
    for pdf in pdfs_raw:
        pdfs.append(crypt.decrypt(pdf.key, pdf.id))

    retrive_file_name = lambda n: os.path.basename(unquote(Path(n).stem))[:-20]
    names = []
    for pdf in pdfs:
        names.append(retrive_file_name(pdf))

    return render_template(
        "view.html", title="View Project", version=version, pdfs=zip(pdfs, names)
    )
