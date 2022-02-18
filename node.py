import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.peers import P2PProtocol
from gunncoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool, P2PProtocol)

async def main():
    alices_public = "034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684"

    # Start the server
    listen_task = asyncio.create_task(server.listen(hostname="127.0.0.1", port=8888))
    connect_task = asyncio.create_task(server.connect_to_network())
    mining_task = asyncio.create_task(server.start_mining(alices_public))

    await listen_task
    await connect_task
    await mining_task
    

asyncio.run(main())