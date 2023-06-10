from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5  # for gravatar
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import BYTEA, ENUM  # Import BYTEA for postgres
from app import db, login
from app.modules.humanizeme import (
    humanize_natural as naturaltime,
    humanize_date as naturaldate,
)
from app.modules.truncate_strings import truncate_string

pdf_version = db.Table(
    "pdf_version",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id")),
    db.Column("version_id", db.Integer, db.ForeignKey("version.vid")),
)

draft_pdf = db.Table(
    "draft_pdf",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id")),
    db.Column("draft_id", db.Integer, db.ForeignKey("draft.did")),
)

rdraft_pdf = db.Table(
    "report_draft_pdf",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id")),
    db.Column("draft_id", db.Integer, db.ForeignKey("reportdraft.rdid")),
)
pdf_report = db.Table(
    "pdf_report",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id")),
    db.Column("report_id", db.Integer, db.ForeignKey("report.rid")),
)

report_version = db.Table(
    "report_version",
    db.Column("report_id", db.Integer, db.ForeignKey("report.rid")),
    db.Column("version_id", db.Integer, db.ForeignKey("version.vid")),
)


class PDF(db.Model):
    __tablename__ = "pdf"

    # General Data
    id = db.Column(BYTEA, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    key = db.Column(BYTEA, nullable=False)

    # PDF relation to Reviewer
    reviewer = db.relationship("Reviewer", back_populates="pdf", uselist=False)

    def __repr__(self):
        return "<PDF {}>".format(self.id)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    uid = db.Column(db.String(16), index=True, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(64))
    birthdate = db.Column(db.Date)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    sex = db.Column(
        ENUM("M", "F", "Other", name="gender_enum", create_type=False), nullable=False
    )
    nationality = db.Column(db.String(32))
    phone = db.Column(db.String(16))
    department = db.Column(db.String(50))
    type = db.Column(
        ENUM("researcher", "reviewer", name="user_type", create_type=False),
        nullable=False,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=64, default="identicon", rating="g"):
        # https://en.gravatar.com/site/implement/images/
        # https://en.gravatar.com/site/implement/hash/
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?s={}&d={}&r={}".format(
            digest, size, default, rating
        )

    # Utils
    def fullname(self):
        return self.first_name + " " + self.last_name

    def format_birth_date(self):
        return self.birthdate.strftime("%Y-%m-%d")

    def time_since_creation(self):
        return naturaldate(self.created_at)

    def time_since_update(self):
        return naturaltime(self.updated_at)

    def time_since_last_seen(self):
        return naturaltime(self.last_seen)

    # End Utils

    def __repr__(self):
        return "<User {}>".format(self.uid)


class Researcher(User):
    __tablename__ = "researcher"
    rsid = db.Column(db.String(16), db.ForeignKey("user.uid"), primary_key=True)
    projects = db.relationship("Project", backref="researcher", lazy=True)

    __mapper_args__ = {"polymorphic_identity": "researcher"}

    def get_id(self):
        return self.rsid

    # End Utils

    def __repr__(self):
        return "<Researcher {}>".format(self.rsid)


class Reviewer(User):
    __tablename__ = "reviewer"

    # General Data
    rvid = db.Column(db.String(16), db.ForeignKey("user.uid"), primary_key=True)
    pdf_id = db.Column(BYTEA, db.ForeignKey("pdf.id"), unique=True, nullable=False)
    pdf = db.relationship("PDF", back_populates="reviewer", uselist=False)

    # Reviewer mapper
    __mapper_args__ = {
        "polymorphic_identity": "reviewer",
    }

    def get_id(self):
        return self.rvid

    def __repr__(self):
        return "<Reviewer {}>".format(self.rvid)


class Project(db.Model):
    __tablename__ = "project"

    # General Data
    pid = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.String(16), db.ForeignKey("researcher.rsid"))

    # Project relation to Version
    versions = db.relationship("Version", backref="project", lazy=True)

    def get_id(self):
        return self.rsid


class Version(db.Model):
    # General Data
    vid = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.Integer, nullable=False)
    project_title = db.Column(db.String(256), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    project_status = db.Column(
        ENUM(
            "Approved",
            "Submitted",
            "Requires changes",
            "Not Approved",
            name="status_enum",
            create_type=False,
        )
    )
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))

    # Version relation to Draft
    draft_id = db.Column(
        db.Integer, db.ForeignKey("draft.did"), unique=True, nullable=False
    )
    draft = db.relationship("Draft", back_populates="version", uselist=False)

    contains = db.relationship(
        "PDF", secondary=pdf_version, backref="version", lazy=True
    )



    # Project versione Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())

    def time_since_creation(self):
        return naturaldate(self.created_at)

    def time_since_update(self):
        return naturaltime(self.updated_at)

    def truncate_desc(self):
        return truncate_string(text=self.project_description, length=200)


class Draft(db.Model):
    did = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Draft relation to PDF
    contains = db.relationship("PDF", secondary=draft_pdf, backref="draft", lazy=True)

    # Draft relation to Version
    version = db.relationship("Version", back_populates="draft", uselist=False)

class Report(db.Model):
    __tablename__ = "report"
    rid = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))
    rvid = db.Column(db.String(16), db.ForeignKey("reviewer.rvid"))
    # Report relation to report_version
    version=db.relationship("Version",secondary=report_version,backref="report",lazy=True)
    # Report relation to reportdraft
    rdraft_id = db.Column(db.Integer, db.ForeignKey("reportdraft.rdid"), unique=True, nullable=True)
    draft = db.relationship("ReportDraft", back_populates="report", uselist=False)

    # Report relation to PDF
    contains = db.relationship("PDF", secondary=pdf_report, backref="report", lazy=True)
    # references to other reports
    reference = db.Column(db.Integer, db.ForeignKey('report.rid'))# Project versione Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow())


    def time_since_creation(self):
        return naturaldate(self.created_at)
    def truncate_desc(self):
        return truncate_string(text=self.body, length=200)



class ReportDraft(db.Model):
    __tablename__ = "reportdraft"
    rdid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    rvid = db.Column(db.String(16), db.ForeignKey("reviewer.rvid"))
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))
    status = db.Column(db.String(256), nullable=False)
    reference = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    # Draft relation to PDF
    contains = db.relationship("PDF", secondary=rdraft_pdf, backref="reportdraft", lazy=True)
    #draft relation to report
    report = db.relationship("Report", back_populates="draft", uselist=False)
    def time_since_creation(self):
        return naturaldate(self.created_at)
    def truncate_desc(self):
        return truncate_string(text=self.body, length=200)


@login.user_loader
def load_researcher(id):
    result = Researcher.query.get(id)
    if result is None:
        return Reviewer.query.get(id)
    return result
