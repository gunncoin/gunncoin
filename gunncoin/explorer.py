
import asyncio
import json
import math
import random
from hashlib import sha256
from time import time
from gunncoin.blockchain import Blockchain
from gunncoin.transactions import block_reward_transaction, create_transaction, validate_transaction

import structlog

logger = structlog.getLogger("Explorer")


class Explorer:
    def __init__(self, blockchain: Blockchain):
      self.blockchain = blockchain
      self.database = {} # {"address": amount}
      self.last_block = 0
      
    def recalculate(self):
      for block in self.blockchain.chain[self.last_block:]:
        for transaction in block["transactions"]:
          self.database[transaction["receiver"]] += transaction["amount"]
          self.database[transaction["sender"]] -= transaction["amount"]

      self.last_block = self.blockchain.last_block["height"]

    def get_balance(self, address):
      return self.database[address]
