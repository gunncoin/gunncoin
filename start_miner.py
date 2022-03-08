import asyncio
import requests
from gunncoin.blockchain import Blockchain
from gunncoin.config.messages import create_config_request
from gunncoin.server.messages import PingMessage, create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.server.peers import P2PProtocol
from gunncoin.server.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from gunncoin.util.constants import CONFIG_PORT, NODE_PORT
from gunncoin.util.utils import get_local_ip
from nacl.signing import SigningKey
import nacl
import structlog
from gunncoin.util.trusted_nodes import TrustedNodes

logger = structlog.getLogger()

async def test():
    config_message = create_config_request("034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684", False, True)

    reader, writer = await asyncio.open_connection("127.0.0.1", CONFIG_PORT)
    await P2PProtocol.send_message(writer, config_message)
    data = await reader.readuntil(b"\n")  # <3>
    decoded_data = data.decode("utf8").strip()  # <4>

    logger.info(decoded_data)
    writer.close()

asyncio.run(test())