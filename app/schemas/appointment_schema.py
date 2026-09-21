from marshmallow import Schema, fields

class AppointmentCreateSchema(Schema):
    slot_id = fields.Integer(required=True)
    reason = fields.String(required=False, allow_none=True)
