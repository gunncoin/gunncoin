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


transaction = create_transaction(alice_private, alices_public, bobs_public, 3)
transaction2 = create_transaction(alice_private, alices_public, bobs_public, 5)

tx_message = create_transaction_message("127.0.0.1", 88, transaction)
tx_message2 = create_transaction_message("127.0.0.1", 88, transaction2)

#req = create_transaction_request(transaction)
req = create_config_request(public_address="034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684", start_mining=True)

block_message =create_block_message("127.0.0.1", 8888, {"height": 5, "transactions": [], "previous_hash": "0000bd60dc6a679df711dfb76f2028338a52a645984148b27405f01018a2f50e", "nonce": "92771b93a3fcde89", "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "timestamp": 1646683687, "hash": "0000bba2b71e0013b34e273d0406f37765d2d5937520efb6583bea3104da9079"})

async def test():

    reader, writer = await asyncio.open_connection(TrustedNodes.get_random_node(), NODE_PORT)
    await P2PProtocol.send_message(writer, block_message)
    data = await reader.readuntil(b"\n")  # <3>
    decoded_data = data.decode("utf8").strip()  # <4>

    logger.info(decoded_data)

asyncio.run(test())