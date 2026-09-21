from marshmallow import Schema, fields, validate, ValidationError, validates_schema

class SlotSchema(Schema):
    id = fields.Integer(dump_only=True)
    doctor_id = fields.Integer(dump_only=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    is_available = fields.Boolean(dump_only=True)

    @validates_schema
    def validate_times(self, data, **kwargs):
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end:
            if start >= end:
                raise ValidationError("start_time doit etre avant end_time", field_name="start_time")
            duration_minutes = (end - start).total_seconds() / 60
            if not (15 <= duration_minutes <= 120):
                raise ValidationError(
                    "la duree du creneau doit etre comprise entre 15 et 120 minutes",
                    field_name="end_time",
                )
