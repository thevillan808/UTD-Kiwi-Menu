from flask import Flask, jsonify
from pydantic import ValidationError

from .db import db
from .extensions import cache


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    cache.init_app(app)

    from .routes import portfolio_bp, security_bp, trade_bp, user_bp
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')
    app.register_blueprint(user_bp, url_prefix='/users')

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({'error': 'Validation Error', 'detail': str(e)}), 422

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({'error': str(e)}), 500

    return app
