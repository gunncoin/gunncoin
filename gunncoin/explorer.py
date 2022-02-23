
import asyncio
import json
import math
import random
from hashlib import sha256
from time import time
from gunncoin.transactions import block_reward_transaction, create_transaction, validate_transaction

import structlog

logger = structlog.getLogger("Explorer")


class Explorer:
    def __init__(self):
        self.database = {}

    def handle_transaction(self, tx):
      return

    def get_balance(self, address):
      return self.database[address]
