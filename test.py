import asyncio
import requests
from gunncoin.explorer.messages import  create_balance_request, create_balance_response, create_transaction_history_request, create_transaction_request, create_transaction_response
from gunncoin.blockchain import Blockchain
from gunncoin.server.messages import PingMessage, create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.server.peers import P2PProtocol
from gunncoin.server.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from gunncoin.util.constants import NODE_PORT
from gunncoin.util.upnp import ask_to_close_port, ask_to_open_port
from gunncoin.util.utils import canyouseeme
from nacl.signing import SigningKey
import nacl
import structlog
from gunncoin.util.trusted_nodes import TrustedNodes

logger = structlog.getLogger()

"""
# Generate secret keys for Alice and Bob
alices_private_key = SigningKey.generate()
bobs_private_key = SigningKey.generate()
# Public keys are generated from the private keys
alices_public_key = alices_private_key.verify_key
bobs_public_key = bobs_private_key.verify_key

alice_private = bytes(alices_private_key).hex()
alices_public = bytes(alices_public_key).hex()

bobs_private = bytes(bobs_private_key).hex()
bobs_public = bytes(bobs_public_key).hex()
"""

alice_private = "bf3f1a7e8911dc9fd0b50e829bb03a301775d0bee630865ad401791e77d21ddc"
alices_public = "034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684"
bobs_private = "9ea1d7796f88ffc8d81e4a345b4dba2af2f2a081e0aa2e22e6b8475486a30baf"
bobs_public = "81acbfc871192f9d1abf4ca6c65b05b8530c62e27e622dad7aa7642560e4a53c"
phone_public = "2437345c606c8f843432a05c75641f323433316972530cba16f6941760ccc6f6"

transaction = create_transaction(alice_private, alices_public, phone_public, 3)
transaction2 = create_transaction(alice_private, alices_public, bobs_public, 5)

tx_message = create_transaction_message("127.0.0.1", 88, transaction)
tx_message2 = create_transaction_message("127.0.0.1", 88, transaction2)

tx_request = create_transaction_request(transaction)

tx_history = create_transaction_history_request("8389437903df537bfa58f9fd767d191cefab3907b07491cb4e382b0f8b19824d")

#req = create_transaction_request(transaction)
req = create_balance_request("81acbfc871192f9d1abf4ca6c65b05b8530c62e27e622dad7aa7642560e4a53c")

async def test():
    reader, writer = await asyncio.open_connection(TrustedNodes.get_random_node(), 48660)
    await P2PProtocol.send_message(writer, tx_request)
    data = await reader.readuntil(b"\n")  # <3>
    decoded_data = data.decode("utf8").strip()  # <4>

    logger.info(decoded_data)

    writer.close()

    #await P2PProtocol.send_message(writer, tx_message2)

async def handle_connection(reader, writer):
    logger.info("NEW CONNECTION!")

#ask_to_open_port(port=15443)
#ask_to_close_port(port=15443)

async def listen( hostname="0.0.0.0"):
    server = await asyncio.start_server(handle_connection, hostname, port=15443)
    logger.info(f"Server listening on port {15443}")

    logger.info("RUNNING TEST")
    logger.info(canyouseeme(port=15443))
    logger.info("Hi")
    async with server:
        await server.serve_forever()


#asyncio.run(listen())
asyncio.run(test())
