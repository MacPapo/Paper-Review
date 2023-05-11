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


class PDF(db.Model):
    __tablename__ = "pdf"

    # General Data
    id = db.Column(BYTEA, primary_key=True)
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
    sex = db.Column(ENUM("M", "F", "Other", name="gender_enum", create_type=False), nullable=False)
    nationality = db.Column(db.String(32))
    phone = db.Column(db.String(16))
    department = db.Column(db.String(50))
    type = db.Column(ENUM("researcher", "reviewer", name="user_type", create_type=False), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

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
    rsid = db.Column(db.String(16), db.ForeignKey('user.uid'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "researcher"
    }

    def get_id(self):
        return self.rsid

    # End Utils

    def __repr__(self):
        return "<User {}>".format(self.rsid)


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
    # General Data
    pid = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.String(16), db.ForeignKey("researcher.rsid"))

    def get_id(self):
        return self.rsid


class Version(db.Model):
    # General Data
    vid = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.Integer, nullable=False)
    project_title = db.Column(db.String(64), nullable=False)
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

    # Project versione Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def time_since_creation(self):
        return naturaldate(self.created_at)

    def time_since_update(self):
        return naturaltime(self.updated_at)

    def truncate_desc(self):
        return truncate_string(text=self.project_description, length=200)


class PDFVersions(db.Model):
    # General Data
    id = db.Column(BYTEA, db.ForeignKey("pdf.id"), primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey("version.vid"), primary_key=True)


@login.user_loader
def load_researcher(id):
    result = Researcher.query.get(id)
    if result is None:
        return Reviewer.query.get(id)
    return result
