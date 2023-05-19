from flask import render_template
from app.blueprints.errors import errors_bp


@errors_bp.app_errorhandler(404)
def handle_404_error(error):
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(500)
def handle_500_error(error):
    return render_template("errors/500.html"), 500
