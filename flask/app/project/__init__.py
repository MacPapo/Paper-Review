from flask import Blueprint

bp = Blueprint("project", __name__)

from app.project import routes
