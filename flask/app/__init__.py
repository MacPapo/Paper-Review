from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bucami'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://moonphase:eclipse@db:5432/paper_review'
app.debug = True

toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
