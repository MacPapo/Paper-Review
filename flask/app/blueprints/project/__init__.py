from flask import Blueprint

bp = Blueprint("project", __name__)

from app.blueprints.project import routes
