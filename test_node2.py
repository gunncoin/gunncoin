import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.peers import P2PProtocol
from gunncoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool, P2PProtocol)

async def main():
    # Start server
    listen_task = asyncio.create_task(server.listen("127.0.0.1", 8886))
    mining_task = asyncio.create_task(server.start_mining("Wallet address"))

    await listen_task
    await mining_task
    

asyncio.run(main())