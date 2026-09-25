from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from app.schemas.user_schema import RegisterSchema, LoginSchema
from app.schemas.slot_schema import SlotSchema
from app.schemas.appointment_schema import AppointmentCreateSchema


def build_spec():
    spec = APISpec(
        title="Teleconsultation API",
        version="1.0.0",
        openapi_version="3.0.3",
        plugins=[MarshmallowPlugin()],
    )

    spec.components.schema("Register", schema=RegisterSchema)
    spec.components.schema("Login", schema=LoginSchema)
    spec.components.schema("Slot", schema=SlotSchema)
    spec.components.schema("AppointmentCreate", schema=AppointmentCreateSchema)

    # Schema de securite JWT : fait apparaitre le bouton "Authorize" dans Swagger UI
    spec.components.security_scheme(
        "bearerAuth",
        {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    )

    spec.path(
        path="/api/v1/auth/register",
        operations={"post": {"requestBody": {"content": {"application/json": {"schema": "Register"}}},
                              "responses": {"201": {"description": "Utilisateur cree"}}}},
    )
    spec.path(
        path="/api/v1/auth/login",
        operations={"post": {"requestBody": {"content": {"application/json": {"schema": "Login"}}},
                              "responses": {"200": {"description": "Token JWT"}}}},
    )
    spec.path(
        path="/api/v1/slots/",
        operations={
            "get": {"responses": {"200": {"description": "Liste paginee des creneaux"}}},
            "post": {"security": [{"bearerAuth": []}],
                      "requestBody": {"content": {"application/json": {"schema": "Slot"}}},
                      "responses": {"201": {"description": "Creneau cree (medecin uniquement)"}}},
        },
    )
    spec.path(
        path="/api/v1/appointments/",
        operations={
            "get": {"security": [{"bearerAuth": []}],
                     "responses": {"200": {"description": "Mes rendez-vous"}}},
            "post": {"security": [{"bearerAuth": []}],
                      "requestBody": {"content": {"application/json": {"schema": "AppointmentCreate"}}},
                      "responses": {"201": {"description": "Rendez-vous reserve (patient uniquement)"}}},
        },
    )
    return spec.to_dict()