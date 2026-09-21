from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate, jwt, ma, cors, limiter
from app.logging_config import configure_logging
from app.security import register_security
from app.errors import register_error_handlers


def create_app(config_name="dev"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    limiter.init_app(app)

    register_security(app)

    from app.routes.auth import auth_bp
    from app.routes.doctors import doctors_bp
    from app.routes.slots import slots_bp
    from app.routes.appointments import appointments_bp
    from app.routes.health import health_bp
    from app.routes.docs import docs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(slots_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(docs_bp)

    register_error_handlers(app)

    with app.app_context():
        from app.models.user import User
        from app.models.doctor import Doctor
        from app.models.patient import Patient
        from app.models.slot import Slot
        from app.models.appointment import Appointment
        if config_name == "test":
            db.create_all()

    return app
