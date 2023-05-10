import logging
from flask import Blueprint

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

from app.auth import routes
