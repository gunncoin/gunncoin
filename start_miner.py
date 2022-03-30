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
    # 8389437903df537bfa58f9fd767d191cefab3907b07491cb4e382b0f8b19824d
    # 2437345c606c8f843432a05c75641f323433316972530cba16f6941760ccc6f6
    config_message = create_config_request("2437345c606c8f843432a05c75641f323433316972530cba16f6941760ccc6f6", False, True)

    reader, writer = await asyncio.open_connection("127.0.0.1", CONFIG_PORT)
    await P2PProtocol.send_message(writer, config_message)
    data = await reader.readuntil(b"\n")  # <3>
    decoded_data = data.decode("utf8").strip()  # <4>

    logger.info(decoded_data)
    writer.close()

asyncio.run(test())