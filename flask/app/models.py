from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5  # for gravatar
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import BYTEA, ENUM  # Import BYTEA for postgres
from app import db, login


class User(db.Model):
    uid = db.Column(db.String(16), index=True, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(64))
    birthdate = db.Column(db.DateTime)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    sex = db.Column(ENUM("M", "F", "Other", name="gender_enum", create_type=False))
    nationality = db.Column(db.String(32))
    phone = db.Column(db.String(16))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    def __repr__(self):
        return "<User {}>".format(self.uid)
    
    def fullname(self):
        return self.first_name + " " + self.last_name
    
    def format_birth_date(self):
        return self.birthdate.strftime('%Y-%m-%d')


class Researcher(UserMixin, db.Model):
    rsid = db.Column(db.String(16), db.ForeignKey("user.uid"), primary_key=True)

    def get_id(self):
        return self.rsid
    
    def is_authenticated(self):
        return self.authenticated
    
    def researcher_fullname(self):
        return User.query.join(Researcher, User.uid == Researcher.rsid).filter_by(rsid=self.rsid).first().fullname()

    def __repr__(self):
        return "<User {}>".format(self.rsid)


@login.user_loader
def load_researcher(rsid):
    return Researcher.query.get(rsid)


class PDF(db.Model):
    id = db.Column(BYTEA, primary_key=True)
    key = db.Column(BYTEA, nullable=False)

    def __repr__(self):
        return "<PDF {}>".format(self.id)
