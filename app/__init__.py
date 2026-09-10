"""Flask application factory."""
from flask import Flask

from config import Config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    from .routes import register_routes
    register_routes(app)
    return app
