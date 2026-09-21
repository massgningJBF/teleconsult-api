from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slots.id"), unique=True, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="booked")  # booked / cancelled

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "slot_id": self.slot_id,
            "reason": self.reason,
            "status": self.status,
            "overdue": False,
        }
