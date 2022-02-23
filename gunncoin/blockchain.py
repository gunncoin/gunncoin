
import asyncio
import json
import math
import random
from hashlib import sha256
from time import time
from gunncoin.transactions import block_reward_transaction, create_transaction, validate_transaction

import structlog

logger = structlog.getLogger("blockchain")


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.target = "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        self.create_genesis_block()

    def create_genesis_block(self):
        # Create the genesis block
        logger.info("Creating genesis block")
        genesis_block = self.create_block(
            mined_by="0",
            height=0,
            transactions=[],
            previous_hash=None,
            nonce="0",
            target="0",
            timestamp=0
        )
        self.chain.append(genesis_block)

    def make_new_block(self, mined_by):
        block = self.create_block(
            mined_by=mined_by,
            height=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.last_block["hash"] if self.last_block else None,
            nonce=format(random.getrandbits(64), "x"),
            target=self.target,
            timestamp=int(time()),
        )

        return block

    @staticmethod
    def create_block(
        mined_by, height, transactions, previous_hash, nonce, target, timestamp=None
    ):
        block = {
            "height": height,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "nonce": nonce,
            "target": target,
            "timestamp": timestamp or int(time()),
        }

        # Get the hash of this new block, and add it to the block
        block["hash"] = Blockchain.hash(block)
        return block

    @staticmethod
    def verify_block_hash(block):
        block_hash = block["hash"]
        data = block.copy()
        data.pop("hash")
        return block_hash == Blockchain.hash(data)

    @staticmethod
    def hash(block):
        # We ensure the dictionary is sorted or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last block in the chain (if there are blocks)
        return self.chain[-1] if self.chain else None

    def has_block(self, block):
        # Does this block exist on our blockchain?
        
        # If the block is newer than what we have, then no
        if self.last_block["height"] < block["height"]:
            return False

        # TODO: Check for conflicts, and figure out a concensus
        return self.chain[block["height"]]["hash"] == block["hash"]

    def valid_block(self, block):
        # Check if a block's hash is less than the target...
        return block["hash"] < self.target

    def add_block(self, block):
        # TODO: Add proper validation logic here!
        self.chain.append(block)

    def add_transaction(self, transaction):
        if(validate_transaction(transaction)):
            self.pending_transactions.append(transaction)
        else:
            logger.error("Invalid transaction: " + json.dumps(transaction))

    def remove_transaction(self, transaction):
        for t in self.pending_transactions:
            if t["signature"] == transaction["signature"]:
                self.pending_transactions.remove(t)
                return

    def recalculate_target(self, block_index):
        """
        Returns the number we need to get below to mine a block
        """
        # Check if we need to recalculate the target
        if block_index % 10 == 0:
            # Expected time span of 10 blocks
            expected_timespan = 10 * 10

            # Calculate the actual time span
            actual_timespan = self.chain[-1]["timestamp"] - self.chain[-10]["timestamp"]

            # Figure out what the offset is
            ratio = actual_timespan / expected_timespan

            # Now let's adjust the ratio to not be too extreme
            ratio = max(0.25, ratio)
            ratio = min(4.00, ratio)

            # Calculate the new target by multiplying the current one by the ratio
            new_target = int(self.target, 16) * ratio

            self.target = format(math.floor(new_target), "x").zfill(64)
            logger.info(f"Calculated new mining target: {self.target}")

        return self.target

    async def get_blocks_after_timestamp(self, timestamp):
        for index, block in enumerate(self.chain):
            if timestamp < block["timestamp"]:
                return self.chain[index:]

    async def mine_new_block(self, public_address: str):
        self.recalculate_target(self.last_block["height"] + 1)

        while True:
            new_block = self.make_new_block(mined_by=public_address)
            if self.valid_block(new_block):
                break

            await asyncio.sleep(0)

        # we found a valid block, reward reset our pending_transactions and add it to our blockchain
        self.pending_transactions = []
        self.chain.append(new_block)
        logger.info("Found a new block: " + json.dumps(new_block))