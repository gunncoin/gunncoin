from importlib.metadata import requires

from marshmallow import Schema, fields


class Config(Schema):
    public_address = fields.Str(required=True)
    upnp = fields.Bool(required=True)
    start_mining = fields.Bool(required=True)