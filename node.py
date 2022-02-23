import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.explorer import Explorer
from gunncoin.server import Server

blockchain = Blockchain()
connection_pool = ConnectionPool()
explorer = Explorer(blockchain)

server = Server(blockchain, connection_pool)

"""
A node is trusted and is used to handle http request for the app.
It is also hard coded for miners to connect to.
Port must be on 8888

TODO: open http port on port 80 and handle get/post requests regarding app
"""

nodes = ["127.0.0.1", "other ip"] # hard coded list of all nodes

async def main():
    # Start the server
    listen_task = asyncio.create_task(server.listen(hostname="127.0.0.1", port=8888))
    #connect_task = asyncio.create_task(server.connect_to_network(nodes[1]))


    await listen_task
    #await connect_task
    

asyncio.run(main())