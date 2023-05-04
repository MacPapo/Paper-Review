from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.modules.firebase import Firebase
from flask_bootstrap import Bootstrap


login = LoginManager()
login.login_view = 'auth.login'

toolbar = DebugToolbarExtension()

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
firebase = Firebase()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bucami"
    app.config["ALLOWED_EXTENSIONS"] = ["pdf"]
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://moonphase:eclipse@db:5432/paper_review"
    app.debug = True

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    return app


from app import models
