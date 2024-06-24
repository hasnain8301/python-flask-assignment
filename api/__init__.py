import pytest
import sentry_sdk
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restx import Api
from loguru import logger
from sentry_sdk.integrations.flask import FlaskIntegration

from .auth.views import auth_namespace
from .candidate.views import candidate_namespace
from .config.config import config_dic
from .db import init_db
from .models.user_models import User


def create_app(config=config_dic["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)
    api = Api(app)

    # JWT
    JWTManager(app)

    # Database
    init_db(app)

    # Loguru
    logger.add("logs/api.log", rotation="500 MB")

    # Sentry
    sentry_sdk.init(
        dsn=app.config["SENTRY_DNS"],
        integrations=[FlaskIntegration()],
    )

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"An error occurred: {e}")
        sentry_sdk.capture_exception(e)
        response = {"error": "Internal Server Error", "message": str(e)}
        return jsonify(response), 500

    api.add_namespace(auth_namespace, path="/auth")
    api.add_namespace(candidate_namespace, path="")
    return app
