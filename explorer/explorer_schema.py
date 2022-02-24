from importlib.metadata import requires
import json
from time import time
from gunncoin.blockchain import Blockchain

from marshmallow import Schema, fields, validates_schema, ValidationError


class Transaction(Schema):
    timestamp = fields.Int(required=True)
    sender = fields.Str(required=True)
    receiver = fields.Str(required=True)
    amount = fields.Int(required=True)
    signature = fields.Str(required=True)

    class Meta:
        ordered = True
        
class Balance(Schema):
    public_address = fields.Str(required=True)