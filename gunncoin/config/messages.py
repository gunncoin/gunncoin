from tracemalloc import start
from marshmallow import Schema, fields, post_load
from marshmallow_oneofschema import OneOfSchema

from gunncoin.config.schema import Config

class ConfigMessage(Schema):
  payload = fields.Nested(Config)

  @post_load
  def add_name(self, data, **kwargs):
    data["name"] = "config"
    return data

class MessageDisambiguation(OneOfSchema):
    type_field = "name"
    type_schemas = {
        "config": ConfigMessage
    }

    def get_obj_type(self, obj):
        if isinstance(obj, dict):
            return obj.get("name")

class BaseSchema(Schema):
    message = fields.Nested(MessageDisambiguation)

def create_config_request(public_address, upnp=False, start_mining=False):
  return BaseSchema().dumps(
    {
      "message": {
        "name": "config",
        "payload": {
          "public_address": public_address,
          "upnp": upnp,
          "start_mining": start_mining,
        }
      }
    }
  )

class ConfigResponse(Schema):
    successful = fields.Bool()

def create_config_response(successful: bool):
    return ConfigResponse().dumps({ "successful": successful })