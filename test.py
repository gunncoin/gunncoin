import asyncio
from gunncoin.blockchain import Blockchain
from gunncoin.messages import create_block_message, create_ping_message, BaseSchema
from gunncoin.schema import Block, Peer, Transaction

some_block = {
    "mined_by": "some public key",
    "height": 123,
    "target": "10",
    "hash": "a52bfa60bc4ad3d3e9571eab8b28370166f2476e0f1026df219bec07a0a9e2e7",
    "previous_hash": "something",
    "nonce": "213",
    "timestamp": 238778621,
}

#message = create_block_message("127.0.0.1", 8888, some_block)
#Block().load(some_block)

ping_message = create_ping_message("127.0.0.1", 8888, 10, 1, True)
message = BaseSchema().loads(ping_message)
print(message)

async def test():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    writer.write(ping_message.encode() + b'\n')
    await writer.drain()

asyncio.run(test())
