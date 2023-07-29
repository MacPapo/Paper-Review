from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime,timedelta
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import BYTEA, ENUM
from app import db, login
from app.modules.humanizeme import (
    humanize_natural as naturaltime,
    humanize_date as naturaldate,
)
from app.modules.truncate_strings import truncate_string

pdf_version = db.Table(
    "pdf_version",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id", ondelete="CASCADE")),
    db.Column("version_id", db.Integer, db.ForeignKey("version.vid", ondelete="CASCADE")),
)

draft_pdf = db.Table(
    "draft_pdf",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id", ondelete="CASCADE")),
    db.Column("draft_id", db.Integer, db.ForeignKey("draft.did", ondelete="CASCADE")),
)

rdraft_pdf = db.Table(
    "report_draft_pdf",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id", ondelete="CASCADE")),
    db.Column("draft_id", db.Integer, db.ForeignKey("reportdraft.rdid", ondelete="CASCADE")),
)

pdf_report = db.Table(
    "pdf_report",
    db.Column("pdf_id", BYTEA, db.ForeignKey("pdf.id", ondelete="CASCADE")),
    db.Column("report_id", db.Integer, db.ForeignKey("report.rid", ondelete="CASCADE")),
)

report_version = db.Table(
    "report_version",
    db.Column("report_id", db.Integer, db.ForeignKey("report.rid", ondelete="CASCADE")),
    db.Column("version_id", db.Integer, db.ForeignKey("version.vid", ondelete="CASCADE")),
)

class Project(db.Model):
    __tablename__ = "project"

    pid = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.String(16), db.ForeignKey("researcher.rsid"))

    researcher = db.relationship("Researcher", backref="project", lazy=True)
    versions = db.relationship("Version", backref="project", lazy=True, cascade="all, delete")

    def get_id(self):
        return self.rsid



class PDF(db.Model):
    __tablename__ = "pdf"

    id = db.Column(BYTEA,primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    key = db.Column(BYTEA, nullable=False)

    reviewer = db.relationship("Reviewer", back_populates="pdf", uselist=False)

    def __repr__(self):
        return "<PDF {}>".format(self.id)

max_birthdate = (datetime.utcnow() - timedelta(days=365 * 18)).date()

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

    comments = db.relationship("Comment", backref="user", lazy=True)
    report_comments = db.relationship("ReportComment", backref="user", lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
    }

    __table_args__ = (
                     db.CheckConstraint("birthdate <= :max_birthdate", name="ck_user_birthdate"),
                         #db.CheckConstraint("username NOT IN (SELECT username FROM user WHERE username IS NOT NULL)", name="ck_user_username"),
                       #db.CheckConstraint("email NOT IN (SELECT email FROM user WHERE email IS NOT NULL)", name="ck_user_email"),
                       #db.CheckConstraint("first_name NOT IN (SELECT last_name FROM user WHERE last_name IS NOT NULL)", name="ck_user_first_name"),
                        #db.CheckConstraint("last_name NOT IN (SELECT first_name FROM user WHERE first_name IS NOT NULL)", name="ck_user_last_name"),
                        db.CheckConstraint("sex IN ('M','F','Other')",name="ck_user_sx_value"),
                        db.CheckConstraint("type IN ('researcher','reviewer')",name="ck_user_type_value"),
                      )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=64, default="identicon", rating="g"):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?s={}&d={}&r={}".format(
            digest, size, default, rating
        )

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

    def __repr__(self):
        return "<User {}>".format(self.uid)


class Researcher(User):
    __tablename__ = "researcher"

    rsid = db.Column(db.String(16), db.ForeignKey("user.uid"), primary_key=True)
    projects = db.relationship("Project", backref="researcher_projects", lazy=True, cascade="all, delete")

    __mapper_args__ = {"polymorphic_identity": "researcher"}

    def get_id(self):
        return self.rsid

    def __repr__(self):
        return "<Researcher {}>".format(self.rsid)


class Reviewer(User):
    __tablename__ = "reviewer"

    rvid = db.Column(db.String(16), db.ForeignKey("user.uid"), primary_key=True)
    pdf_id = db.Column(BYTEA, db.ForeignKey("pdf.id",ondelete='CASCADE'), unique=True, nullable=False)
    pdf = db.relationship("PDF", back_populates="reviewer", uselist=False,cascade='all, delete')

    __mapper_args__ = {
        "polymorphic_identity": "reviewer",
    }

    def get_id(self):
        return self.rvid

    def __repr__(self):
        return "<Reviewer {}>".format(self.rvid)


class Version(db.Model):
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
    pid= db.Column(db.Integer, db.ForeignKey("project.pid",ondelete='CASCADE'))

    draft_id = db.Column(
        db.Integer, db.ForeignKey("draft.did"), unique=True, nullable=False
    )
    draft = db.relationship("Draft", back_populates="version", uselist=False, cascade="all, delete")

    contains = db.relationship(
        "PDF", secondary=pdf_version, backref="version", lazy=True, cascade="all, delete"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    __table_args__ = (
        db.CheckConstraint("version_number > 0", name="ck_version_number"),
        db.CheckConstraint("project_status IN ('Approved','Submitted','Requires changes','Not Approved')", name="ck_project_status"),
        #db.CheckConstraint("project_title NOT IN (SELECT project_title FROM version WHERE project_title IS NOT NULL)", name="ck_project_title"),
        db.Index("version_index","project_title","version_number"),
    )

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

    contains = db.relationship("PDF", secondary=draft_pdf, backref="draft", lazy=True, cascade="all, delete")

    version = db.relationship("Version", back_populates="draft", uselist=False, cascade="all, delete")

    __table_args__ = (
        #db.CheckConstraint("title NOT IN (SELECT project_title FROM version WHERE project_title IS NOT NULL)", name="ck_draft_title"),
        db.Index("draft_index","title"),
    )

class Report(db.Model):
    __tablename__ = "report"
    rid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey("project.pid",ondelete='CASCADE'))
    rvid = db.Column(db.String(16), db.ForeignKey("reviewer.rvid"))

    version = db.relationship("Version", secondary=report_version, backref="report", lazy=True, cascade="all, delete")

    rdraft_id = db.Column(db.Integer, db.ForeignKey("reportdraft.rdid",ondelete='CASCADE'), unique=True, nullable=True)
    draft = db.relationship("ReportDraft", back_populates="report", uselist=False, cascade="all, delete")

    contains = db.relationship("PDF", secondary=pdf_report, backref="report", lazy=True, cascade="all, delete")
    reference = db.Column(db.Integer, db.ForeignKey('report.rid',ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    __table_args__ = (
        db.Index("report_index","pid","rvid","title"),
    )

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
    pid = db.Column(db.Integer, db.ForeignKey("project.pid",ondelete='CASCADE'))
    status = db.Column(db.String(256), nullable=False)
    reference = db.Column(db.Integer,nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    contains = db.relationship("PDF", secondary=rdraft_pdf, backref="reportdraft", lazy=True, cascade="all, delete")

    report = db.relationship("Report", back_populates="draft", uselist=False, cascade="all, delete")

    __table_args__ = (
        db.CheckConstraint("status IN ('Approved','Submitted','Requires changes','Not Approved')", name="ck_report_status"),
        db.Index("reportdraft_index","pid","rvid","title"),
    )

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


class Comment(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    version_ref = db.Column(db.Integer, nullable=False)

    #Comment relation to User
    uid = db.Column(db.String(16), db.ForeignKey("user.uid"))

    #Comment relation to Project
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))

    __table_args__ = (
        db.Index("comment_index","pid","version_ref"),
    )
    def time_since_creation(self):
        return naturaldate(self.created_at)

class ReportComment(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    version_ref = db.Column(db.Integer, nullable=False)

    #Comment relation to User
    uid = db.Column(db.String(16), db.ForeignKey("user.uid"))

    #Comment relation to Project
    rid = db.Column(db.Integer, db.ForeignKey("report.rid"))

    __table_args__ = (
        db.Index("reportcomment_index","rid","version_ref"),
    )

    def time_since_creation(self):
        return naturaldate(self.created_at)
#utente non si può iscrivere due volte
#il reviewer che fa report non può essere researcher del progetto
#se versione del commento dopo, la data deve esserre maggiore
#report non fa reference a se stesso
#se progetto è stato concluso , non possiamo fare altro (trigger)
#projetto se uguale allora titolo è uguale
