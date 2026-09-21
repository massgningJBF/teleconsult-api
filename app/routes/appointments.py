from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.extensions import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.schemas.appointment_schema import AppointmentCreateSchema
from app.services import appointment_service
from app.auth_helpers import role_required

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/v1/appointments")
appointment_schema = AppointmentCreateSchema()


@appointments_bp.post("/")
@role_required("patient")
def book_appointment():
    data = appointment_schema.load(request.get_json() or {})
    patient = Patient.query.filter_by(user_id=int(get_jwt_identity())).first()
    if patient is None:
        return jsonify({"error": "not_found", "message": "profil patient introuvable"}), 404

    appointment = appointment_service.book_appointment(
        patient_id=patient.id, slot_id=data["slot_id"], reason=data.get("reason")
    )
    if appointment is None:
        return jsonify({"error": "not_found", "message": "creneau introuvable"}), 404

    return jsonify(appointment_service.appointment_to_dict(appointment)), 201


@appointments_bp.get("/")
@role_required("patient", "doctor")
def list_appointments():
    role = get_jwt().get("role")
    user_id = int(get_jwt_identity())

    if role == "patient":
        patient = Patient.query.filter_by(user_id=user_id).first()
        if patient is None:
            return jsonify({"items": []}), 200
        appointments = appointment_service.list_appointments_for_patient(patient.id)
        items = [appointment_service.appointment_to_dict(a) for a in appointments]
    else:
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        if doctor is None:
            return jsonify({"items": []}), 200
        appointments = appointment_service.list_appointments_for_doctor(doctor.id)
        items = [appointment_service.appointment_to_dict(a, include_patient=True) for a in appointments]

    return jsonify({"items": items}), 200


@appointments_bp.post("/<int:appointment_id>/cancel")
@role_required("patient")
def cancel_appointment(appointment_id):
    user_id = int(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=user_id).first()
    appointment = db.session.get(Appointment, appointment_id)

    if appointment is None or patient is None or appointment.patient_id != patient.id:
        return jsonify({"error": "not_found"}), 404

    appointment = appointment_service.cancel_appointment(appointment)
    return jsonify(appointment_service.appointment_to_dict(appointment)), 200
