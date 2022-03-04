
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
from gunncoin.config.messages import BaseSchema, create_config_response
from gunncoin.transactions import validate_transaction
from gunncoin.util.constants import CONFIG_PORT

from marshmallow.exceptions import MarshmallowError
import structlog

logger = structlog.getLogger("Config")

class Config:
    def __init__(self, server):
        from gunncoin.server.server import Server
        self.server: Server = server

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
        server = await asyncio.start_server(self.handle_connection, "0.0.0.0", CONFIG_PORT)
        logger.info(f"Config listening on port {CONFIG_PORT}")

        async with server:
          await server.serve_forever()

    @staticmethod
    async def send_message(writer, message):
        writer.write(message.encode() + b"\n")

    async def handle_message(self, message, writer: StreamWriter):
        message_handlers = {
            "config": self.handle_config_request
        }

        handler = message_handlers.get(message["name"])
        if not handler:
            raise Exception("Missing handler for message")

        await handler(message, writer)

    async def handle_config_request(self, message, writer):
        """
        Balance request on mobile app
        """
        logger.info("Received config request")

        payload = message["payload"]
        public_address: str = payload["public_address"]
        upnp: bool = payload["upnp"]
        start_mining: bool = payload["start_mining"]

        if(start_mining):
            asyncio.create_task(self.server.start_mining(public_address))

        logger.info("TODO")

        # Send back response
        res = create_config_response(True)
        await P2PProtocol.send_message(writer, res)