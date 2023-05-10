import logging
from flask import Blueprint
from app.errors.handlers import not_found_error, internal_error

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

bp.register_error_handler(404, not_found_error)
bp.register_error_handler(500, internal_error)

from app.auth import routes
