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

class Block(Schema):
    mined_by = fields.Str(required=False)
    transactions = fields.List(fields.Nested(Transaction()))
    height = fields.Int(required=True)
    target = fields.Str(required=True)
    hash = fields.Str(required=True)
    previous_hash = fields.Str(required=True)
    nonce = fields.Str(required=True)
    timestamp = fields.Int(required=True)

    class Meta:
        ordered = True

    @validates_schema
    def validate_hash(self, data, **kwargs):
        block = data.copy()
        block.pop("hash")

        if data["hash"] != Blockchain.hash(block):
            raise ValidationError("Fraudulent block: hash is wrong")

class Peer(Schema):
    ip = fields.Str(required=True)
    port = fields.Int(required=True)
    last_seen = fields.Int(missing=lambda: int(time()))


class Ping(Schema):
    block_height = fields.Int()
    peer_count = fields.Int()
    is_miner = fields.Bool()

class Consensus(Schema):
    blocks = fields.List(fields.Nested(Block()))