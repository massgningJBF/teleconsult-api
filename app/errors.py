from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

from app.services.appointment_service import SlotUnavailableError, CancellationWindowError


def register_error_handlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    @app.errorhandler(SlotUnavailableError)
    def handle_slot_unavailable(err):
        return jsonify({"error": "conflict", "message": str(err)}), 409

    @app.errorhandler(CancellationWindowError)
    def handle_cancellation_window(err):
        return jsonify({"error": "forbidden", "message": str(err)}), 403

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return jsonify({"error": err.name.lower().replace(" ", "_"), "message": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Erreur non geree")
        return jsonify({"error": "internal_server_error", "message": "une erreur est survenue"}), 500
