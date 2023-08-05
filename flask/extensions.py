from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from faker import Faker
from app.modules.firebase import Firebase

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
firebase = Firebase()
fake = Faker()
