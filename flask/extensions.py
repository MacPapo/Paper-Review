from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

from app.modules.firebase import Firebase

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
toolbar = DebugToolbarExtension()
firebase = Firebase()
