from flask import Blueprint, jsonify
from app.models.doctor import Doctor

doctors_bp = Blueprint("doctors", __name__, url_prefix="/api/v1/doctors")


@doctors_bp.get("/")
def list_doctors():
    doctors = Doctor.query.order_by(Doctor.name).all()
    return jsonify({"items": [d.to_dict() for d in doctors]}), 200


@doctors_bp.get("/<int:doctor_id>")
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(doctor.to_dict()), 200
