from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.modules.firebase import Firebase
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "bucami"
app.config["ALLOWED_EXTENSIONS"] = ["pdf"]
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://moonphase:eclipse@db:5432/paper_review"
app.debug = True

login = LoginManager(app)
login.login_view = "login"

toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
firebase = Firebase()

from app import routes, models, errors
