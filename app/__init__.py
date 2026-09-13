"""Flask application factory."""
from flask import Flask, render_template

from config import Config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    from .routes import register_routes
    register_routes(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404,
                             error_message="The page you're looking for doesn't exist or has been moved."), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html',
                             error_code=500,
                             error_message="An unexpected error occurred. Please try again later."), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return render_template('error.html',
                             error_code=503,
                             error_message="The service is temporarily unavailable. Please try again later."), 503
    
    return app
