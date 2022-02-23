import asyncio
import structlog

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.explorer import Explorer
from gunncoin.server import Server

logger = structlog.getLogger()

blockchain = Blockchain()
connection_pool = ConnectionPool()
explorer = Explorer(blockchain)

server = Server(blockchain, connection_pool)

"""
A node is trusted and is used to handle http request for the app.
It is also hard coded for miners to connect to.
Port must be on 4866 (GUNN)

TODO: open http port on port 80 and handle get/post requests regarding app
"""

nodes = ["127.0.0.1", "other ip"] # hard coded list of all nodes

async def main():
    # Start the server
    listen_task = asyncio.create_task(server.listen(port=4866))
    #connect_task = asyncio.create_task(server.connect_to_network(nodes[1]))

    await asyncio.sleep(15)
    explorer.recalculate()
    logger.info(explorer.database)

    await listen_task
    #await connect_task

    

asyncio.run(main())