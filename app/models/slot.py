from app.extensions import db


class Slot(db.Model):
    __tablename__ = "slots"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    appointment = db.relationship("Appointment", backref="slot", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "is_available": self.is_available,
        }
