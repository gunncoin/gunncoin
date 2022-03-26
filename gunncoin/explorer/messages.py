from gunncoin.server.schema import Transaction
from gunncoin.server.types import TransactionType
from marshmallow import Schema, fields, post_load
from marshmallow_oneofschema import OneOfSchema

from gunncoin.explorer.schema import Balance, TransactionHistoryMessage



class BalanceMessage(Schema):
  payload = fields.Nested(Balance)

  @post_load
  def add_name(self, data, **kwargs):
    data["name"] = "balance"
    return data

class TransactionMessage(Schema):
    payload = fields.Nested(Transaction)

    @post_load
    def add_name(self, data, **kwargs):
        data["name"] = "transaction"
        return data

class MessageDisambiguation(OneOfSchema):
    type_field = "name"
    type_schemas = {
        "balance": BalanceMessage,
        "transaction": TransactionMessage,
        "tx_history": TransactionHistoryMessage
    }

    def get_obj_type(self, obj):
        if isinstance(obj, dict):
            return obj.get("name")

class BaseSchema(Schema):
    message = fields.Nested(MessageDisambiguation)

def create_balance_request(public_address):
  return BaseSchema().dumps(
    {
        "message": {
            "name": "balance",
            "payload": {
                "public_address": public_address
            }
        }
    }
  )

def create_transaction_history_request(public_address):
    return BaseSchema().dumps(
        {
            "message": {
            "name": "tx_history",
            "payload": {
                "public_address": public_address
            }
        }
    }
    )

def create_transaction_request(tx):
    return BaseSchema().dumps(
        {
            "message": {
                "name": "transaction",
                "payload": tx,
            },
        }
    )

class BalanceResponse(Schema):
    balance = fields.Int()

class TransactionHistoryMessage(Schema):
    transactions = fields.List(fields.Nested(Transaction()))

class TransactionResponse(Schema):
    successful: fields.Bool()

def create_balance_response(balance: int):
    return BalanceResponse().dumps({ "balance": balance })

def create_transaction_history_response(transactions: list[TransactionType]):
    return TransactionHistoryMessage().dumps({ "transactions": transactions })

def create_transaction_response(successful: bool):
    return TransactionResponse().dumps({ "successful": successful })