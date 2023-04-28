from werkzeug.security import generate_password_hash, check_password_hash

# Import BYTEA for postgres
from sqlalchemy.dialects.postgresql import BYTEA

from datetime import datetime
from app import db #, login

class PDF(db.Model):
    id = db.Column(BYTEA, primary_key=True)
    key = db.Column(BYTEA, nullable=False)

    def __repr__(self):
        return "<PDF {}>".format(self.id)
