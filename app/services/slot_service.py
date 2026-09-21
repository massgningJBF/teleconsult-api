from app.extensions import db
from app.models.slot import Slot
from app.models.doctor import Doctor

MAX_PER_PAGE = 100


def create_slot(doctor_id, start_time, end_time):
    slot = Slot(doctor_id=doctor_id, start_time=start_time, end_time=end_time, is_available=True)
    db.session.add(slot)
    db.session.commit()
    return slot


def list_slots(page=1, per_page=10, doctor_id=None, available_only=False):
    per_page = min(per_page, MAX_PER_PAGE)
    query = Slot.query
    if doctor_id:
        query = query.filter(Slot.doctor_id == doctor_id)
    if available_only:
        query = query.filter(Slot.is_available.is_(True))
    return query.order_by(Slot.start_time).paginate(page=page, per_page=per_page, error_out=False)


def get_slot(slot_id):
    return db.session.get(Slot, slot_id)


def get_doctor_by_user_id(user_id):
    return Doctor.query.filter_by(user_id=user_id).first()
