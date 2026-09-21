from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    role = fields.String(required=True, validate=validate.OneOf(["patient", "doctor"]))
    name = fields.String(required=True, validate=validate.Length(min=1))
    specialty = fields.String(required=False)  # requis si role=doctor, verifie dans le service

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
