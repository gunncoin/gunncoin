import asyncio
from gunncoin.blockchain import Blockchain
from gunncoin.messages import create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from nacl.signing import SigningKey
import nacl

# Generate secret keys for Alice and Bob
alices_private_key = SigningKey.generate()
bobs_private_key = SigningKey.generate()
# Public keys are generated from the private keys
alices_public_key = alices_private_key.verify_key
bobs_public_key = bobs_private_key.verify_key

alice_private = bytes(alices_private_key).hex()
alices_public = bytes(alices_public_key).hex()

bobs_public = bytes(bobs_public_key).hex()

fake_transaction = create_transaction(alice_private, alices_public, bobs_public, 10)
b = Blockchain()
b.add_transaction(fake_transaction)
block = b.make_random_block()

message = create_block_message("127.0.0.1", 8888, block)
block = Block().load(block)


ping_message = create_ping_message("127.0.0.1", 8888, 10, 1, True)
message = BaseSchema().loads(ping_message)
async def mine_block():
    bc = Blockchain()
    await bc.mine_new_block()
    await bc.mine_new_block()

async def test():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    writer.write(ping_message.encode() + b'\n')
    await writer.drain()

    data = await reader.readuntil(b"\n")  # <3>
    print(data)




#asyncio.run(mine_block())
