from app.extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False)

    slots = db.relationship("Slot", backref="doctor", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "email": self.email,
        }
