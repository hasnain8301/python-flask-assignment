from flask import current_app, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.user_models import AuthorizedUser, User

auth_namespace = Namespace("Auth", description="Authentication related operations")

# Validator
register_model = auth_namespace.model(
    "register",
    {
        "username": fields.String(required=True, description="username"),
        "password": fields.String(required=True, description="password"),
    },
)


@auth_namespace.route("/register")
class Register(Resource):
    @auth_namespace.expect(register_model)
    def post(self):
        user_data = request.json
        user = User(**user_data)
        user.password = generate_password_hash(user.password)
        current_app.db["users"].insert_one(user.model_dump(by_alias=True))
        logger.info(f"User registered: {user.username}")
        return user.model_dump(by_alias=True), 201


@auth_namespace.route("/login")
class Login(Resource):
    @auth_namespace.expect(register_model)
    def post(self):
        data = request.json
        authorized_user = AuthorizedUser(**data)
        user = current_app.db["users"].find_one({"username": authorized_user.username})
        if user and check_password_hash(user["password"], authorized_user.password):
            authorized_user.access_token = create_access_token(
                identity=str(user["_id"])
            )
            logger.info(f"User logged in: {authorized_user.username}")
            return authorized_user.model_dump(by_alias=True, exclude="password"), 200
        logger.warning(f"Failed login attempt for username: {authorized_user.username}")
        return {"error": "Invalid credentials"}, 401


@auth_namespace.route("/protected")
class Protected(Resource):
    @jwt_required()
    @auth_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    def get(self):
        current_user = get_jwt_identity()
        logger.info(f"Accessed protected route by user ID: {current_user}")
        return {"logged_in_as": current_user}, 200
