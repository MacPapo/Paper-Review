from flask import Blueprint
from app.errors.handlers import not_found_error, internal_error

bp = Blueprint("project", __name__)

bp.register_error_handler(404, not_found_error)
bp.register_error_handler(500, internal_error)

from app.project import routes
