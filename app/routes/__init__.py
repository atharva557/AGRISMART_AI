"""Register module routes; coordinate shared changes with integration."""
from .main import bp as main
from .disease import bp as disease
from .advisory import bp as advisory
from .assistant import bp as assistant


def register_routes(app):
    for blueprint in (main, disease, advisory, assistant):
        app.register_blueprint(blueprint)
