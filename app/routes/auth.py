from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.schemas.user_schema import RegisterSchema, LoginSchema
from app.services import auth_service
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.post("/register")
def register():
    data = register_schema.load(request.get_json() or {})
    user, error = auth_service.register(
        email=data["email"],
        password=data["password"],
        role=data["role"],
        name=data["name"],
        specialty=data.get("specialty"),
    )
    if error:
        return jsonify({"error": "conflict", "message": error}), 409
    return jsonify(user.to_dict()), 201


@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    data = login_schema.load(request.get_json() or {})
    user = auth_service.authenticate(data["email"], data["password"])
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401

    claims = {"role": user.role}
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)
    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    role = get_jwt().get("role")
    new_token = create_access_token(identity=identity, additional_claims={"role": role})
    return jsonify({"access_token": new_token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not_found"}), 404
    return jsonify(user.to_dict()), 200
