from flask import Blueprint

errors_bp = Blueprint("errors", __name__)

from app.blueprints.errors import views
