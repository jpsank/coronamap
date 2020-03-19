from flask import render_template
from werkzeug.exceptions import RequestEntityTooLarge

from app.blueprints.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
