
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
          receiver = transaction["receiver"]
          sender = transaction["sender"]
          amount = transaction["amount"]

          logger.info(amount)

          if not receiver in self.database:
            self.database[receiver] = 0

          if not sender in self.database:
            self.database[sender] = 0

          self.database[receiver] += amount
          self.database[sender] -= amount

      self.last_block = self.blockchain.last_block["height"]

    def get_balance(self, address):
      return self.database[address]
