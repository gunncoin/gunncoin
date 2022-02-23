import asyncio
from gunncoin.blockchain import Blockchain
from gunncoin.messages import PingMessage, create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.peers import P2PProtocol
from gunncoin.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from nacl.signing import SigningKey
import nacl
import structlog

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


transaction = create_transaction(alice_private, alices_public, bobs_public, 10)
transaction2 = create_transaction(alice_private, alices_public, bobs_public, 20)

logger.info(transaction)

tx_message = create_transaction_message("127.0.0.1", 88, transaction)
tx_message2 = create_transaction_message("127.0.0.1", 88, transaction2)

logger.info(tx_message)

async def test():
    reader, writer = await asyncio.open_connection('127.0.0.1', 4866)
    await P2PProtocol.send_message(writer, tx_message)
    await asyncio.sleep(2)
    await P2PProtocol.send_message(writer, tx_message2)

asyncio.run(test())
