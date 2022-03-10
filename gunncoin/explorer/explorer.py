
import asyncio
from asyncio import StreamReader, StreamWriter
import json
import math
import random
from hashlib import sha256
from time import time
from gunncoin.server.messages import create_transaction_message

from gunncoin.blockchain import Blockchain
from gunncoin.server.peers import P2PProtocol
from gunncoin.transactions import validate_transaction
from gunncoin.explorer.messages import BaseSchema, create_balance_request, create_balance_response, create_transaction_response
from gunncoin.util.constants import EXPLORER_PORT

from marshmallow.exceptions import MarshmallowError
import structlog

logger = structlog.getLogger("Explorer")

class Explorer:
    def __init__(self, server):
        from gunncoin.server.server import Server
        self.server: Server = server
        self.blockchain = self.server.blockchain
        self.database = {} # {"address": amount}
        self.last_block_height = 0
      
    def recalculate(self):
        """
        Recalculates balance of all address's
        """

        if self.last_block_height == self.blockchain.last_block["height"]:
            # Already up to date
            return

        for block in self.blockchain.chain[self.last_block_height:]:
            for transaction in block["transactions"]:
                receiver = transaction["receiver"]
                sender = transaction["sender"]
                amount = transaction["amount"]

                if not receiver in self.database:
                    self.database[receiver] = 0
                self.database[receiver] += amount

                # Don't account for mined blocks
                if sender == "0":
                    continue

                if not sender in self.database:
                    self.database[sender] = 0
                self.database[sender] -= amount

        self.last_block_height = self.blockchain.last_block["height"]

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        while True:
            try:
                # Wait forever on new data to arrive
                data = await reader.readuntil(b"\n")
                decoded_data = data.decode("utf8").strip()

                try:
                    message = BaseSchema().loads(decoded_data)
                except MarshmallowError:
                    logger.info("Received unreadable message", peer=writer)
                    break

                # ...and handle the message
                await self.handle_message(message["message"], writer)
                await writer.drain()

                if writer.is_closing():
                    break

            except (asyncio.exceptions.IncompleteReadError, ConnectionError) as e:
                # An error happened, break out of the wait loop
                logger.error(e)
                break

        # The connection has closed. Let's clean up...
        writer.close()
        await writer.wait_closed()

    async def setup(self):
        listen_task = asyncio.create_task(self.listen())
        await listen_task

    async def listen(self):
        server = await asyncio.start_server(self.handle_connection, "0.0.0.0", EXPLORER_PORT)
        logger.info(f"Explorer listening on port {EXPLORER_PORT}")

        async with server:
          await server.serve_forever()

    def get_balance(self, address):
        return self.database[address]

    @staticmethod
    async def send_message(writer, message):
        writer.write(message.encode() + b"\n")

    async def handle_message(self, message, writer: StreamWriter):
        message_handlers = {
            "transaction": self.handle_transaction_request,
            "balance": self.handle_balance_request
        }

        handler = message_handlers.get(message["name"])
        if not handler:
            raise Exception("Missing handler for message")

        await handler(message, writer)

    async def handle_transaction_request(self, message, writer):
        """
        Transaction request by mobile app
        """
        logger.info("Received transaction")

        self.recalculate()

        # Extract transaction data
        tx = message["payload"]
        
        # Check for balance
        if not (tx["sender"] in self.database and self.database[tx["sender"]] > tx["amount"]):
            logger.warning("Insufficient funds")

            # It did not work for some reason
            res = create_transaction_response(False)
            await P2PProtocol.send_message(writer, res)

            return

        # Send it to our networked server to send to other peers if its a valid transaction
        if validate_transaction(tx):
            for peer in self.server.connection_pool.get_alive_peers(20):
                await self.send_message(
                    peer[1],
                        create_transaction_message(
                            self.server.external_ip, self.server.external_port, tx
                        ),
                    )
            
            # It worked, so we let our dude know
            message = create_transaction_response(True)
            await P2PProtocol.send_message(writer, message)
        else:
            logger.warning("Received invalid transaction")

            # It did not work for some reason
            res = create_transaction_response(False)
            await P2PProtocol.send_message(writer, res)

    async def handle_balance_request(self, message, writer):
        """
        Balance request on mobile app
        """
        logger.info("Received balance request")

        self.recalculate()

        # Write back balance response
        public_address = message["payload"]["public_address"]
        res = create_balance_response(self.database[public_address] if public_address in self.database else 0)
        await P2PProtocol.send_message(writer, res)