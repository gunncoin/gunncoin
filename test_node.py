import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.peers import P2PProtocol
from gunncoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool, P2PProtocol)

async def main():
    # Start the server
    listen_task = asyncio.create_task(server.listen(hostname="127.0.0.1", port=8887))

    await listen_task
    

asyncio.run(main())