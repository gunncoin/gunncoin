import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.peers import P2PProtocol
from gunncoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool, P2PProtocol)

async def main():
    bobs_public = "81acbfc871192f9d1abf4ca6c65b05b8530c62e27e622dad7aa7642560e4a53c"

    # Start the server
    listen_task = asyncio.create_task(server.listen(hostname="127.0.0.1", port=8887))
    connect_task = asyncio.create_task(server.connect_to_network())
    mining_task = asyncio.create_task(server.start_mining(bobs_public))

    await listen_task
    await connect_task
    await mining_task
    

asyncio.run(main())