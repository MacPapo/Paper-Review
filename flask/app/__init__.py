from flask import Flask
from extensions import db, migrate, login, bootstrap, toolbar, firebase, fake
from app.blueprints.errors import errors_bp
from app.blueprints.project import bp as project_bp
from app.blueprints.main import bp as main_bp
from app.blueprints.auth import bp as auth_bp
from config import Config
from app.trigger_creation import create_triggers
def create_app():
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(Config)
    app.debug = True

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    toolbar.init_app(app)
    firebase.init_app(app)
    fake.init_app(app)

    app.register_blueprint(errors_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    with app.app_context():
        create_triggers()
    return app
