from importlib.metadata import requires
import json
from time import time
from gunncoin.blockchain import Blockchain

from marshmallow import Schema, fields, validates_schema, ValidationError
        
class Balance(Schema):
    public_address = fields.Str(required=True)

class TransactionHistoryMessage(Schema):
    public_address = fields.Str(required=True)