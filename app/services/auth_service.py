from app.extensions import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient


def register(email, password, role, name, specialty=None):
    if User.query.filter_by(email=email).first():
        return None, "email deja utilise"
    if role == "doctor" and not specialty:
        return None, "specialty requis pour un medecin"

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # recupere user.id avant le commit

    if role == "doctor":
        profile = Doctor(user_id=user.id, name=name, specialty=specialty, email=email)
    else:
        profile = Patient(user_id=user.id, name=name, email=email)
    db.session.add(profile)
    db.session.commit()
    return user, None


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None
