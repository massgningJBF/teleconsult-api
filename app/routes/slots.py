from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.extensions import db
from app.schemas.slot_schema import SlotSchema
from app.services import slot_service
from app.auth_helpers import role_required

slots_bp = Blueprint("slots", __name__, url_prefix="/api/v1/slots")
slot_schema = SlotSchema()


@slots_bp.get("/")
def list_slots():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    doctor_id = request.args.get("doctor_id", type=int)
    available_only = request.args.get("available", type=str) == "true"

    pagination = slot_service.list_slots(
        page=page, per_page=per_page, doctor_id=doctor_id, available_only=available_only
    )
    return jsonify({
        "items": [s.to_dict() for s in pagination.items],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "total": pagination.total,
        },
    }), 200


@slots_bp.post("/")
@role_required("doctor")
def create_slot():
    data = slot_schema.load(request.get_json() or {})
    doctor = slot_service.get_doctor_by_user_id(int(get_jwt_identity()))
    if doctor is None:
        return jsonify({"error": "not_found", "message": "profil medecin introuvable"}), 404

    slot = slot_service.create_slot(doctor.id, data["start_time"], data["end_time"])
    return jsonify(slot.to_dict()), 201
