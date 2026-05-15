import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from .db import db
from .extensions import cache


def _configure_logging(app):
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'app.log')

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # Also apply to the root logger so other modules (auth, services) are captured
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.DEBUG)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    cache.init_app(app)
    CORS(app, origins=['http://localhost:5173'])
    _configure_logging(app)

    from .routes import portfolio_bp, security_bp, trade_bp, user_bp
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')
    app.register_blueprint(user_bp, url_prefix='/users')

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        app.logger.exception('Validation error: %s', e)
        return jsonify({'error': 'Validation Error', 'detail': str(e)}), 422

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception('Unhandled exception: %s', e)
        return jsonify({'error': str(e)}), 500

    return app
