from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db #, login

class PDF(db.Model):
    id = db.Column(db.String(512), primary_key=True)
    key = db.Column(db.String(128))

    def __repr__(self):
        return "<PDF {}>".format(self.id)
