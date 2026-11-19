"""Flask application factory."""
from flask import Flask

from . import config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024

    from .routes import bp
    app.register_blueprint(bp)
    return app
