from datetime import datetime, timedelta
from app.extensions import db
from app.models.appointment import Appointment
from app.models.slot import Slot
from app.models.patient import Patient
from app.models.doctor import Doctor


class SlotUnavailableError(Exception):
    pass


class CancellationWindowError(Exception):
    pass


def book_appointment(patient_id, slot_id, reason=None):
    slot = db.session.get(Slot, slot_id)
    if slot is None:
        return None
    if not slot.is_available:
        raise SlotUnavailableError("ce creneau n'est plus disponible")

    appointment = Appointment(patient_id=patient_id, slot_id=slot_id, reason=reason, status="booked")
    slot.is_available = False
    db.session.add(appointment)
    db.session.commit()
    return appointment


def cancel_appointment(appointment, actor_patient_id=None):
    slot = db.session.get(Slot, appointment.slot_id)
    if datetime.utcnow() > slot.start_time - timedelta(hours=24):
        raise CancellationWindowError("annulation impossible a moins de 24h du rendez-vous")

    appointment.status = "cancelled"
    slot.is_available = True
    db.session.commit()
    return appointment


def list_appointments_for_patient(patient_id):
    return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.id.desc()).all()


def list_appointments_for_doctor(doctor_id):
    return (
        Appointment.query.join(Slot, Appointment.slot_id == Slot.id)
        .filter(Slot.doctor_id == doctor_id)
        .order_by(Appointment.id.desc())
        .all()
    )


def appointment_to_dict(appointment, include_patient=False):
    data = appointment.to_dict()
    slot = db.session.get(Slot, appointment.slot_id)
    data["slot"] = slot.to_dict() if slot else None
    data["overdue"] = bool(
        slot and appointment.status == "booked" and slot.start_time < datetime.utcnow()
    )
    if include_patient:
        patient = db.session.get(Patient, appointment.patient_id)
        data["patient"] = patient.to_dict() if patient else None
    return data
