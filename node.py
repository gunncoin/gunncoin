import asyncio
from cmath import exp
import structlog

from gunncoin.blockchain import Blockchain
from gunncoin.server.connections import ConnectionPool
from gunncoin.explorer.explorer import Explorer
from gunncoin.server.server import Server

logger = structlog.getLogger()

blockchain = Blockchain()
connection_pool = ConnectionPool()

server = Server(blockchain, connection_pool)
explorer = Explorer(server)

"""
A node is trusted and is used to handle http request for the app.
It is also hard coded for miners to connect to.
Port must be on 4866 (GUNN)

Port 48660 (GUNN0) is used to handle get/post requests regarding app
We send a transaction request from a phone to here, which will then check for sufficient balance
The message will assume that balance is correct, as signiture cannot be forged and node already verified (node is trusted)

To install...
pyinstaller --onefile node.py --hidden-import=_cffi_backend
"""

async def main():
    # Start the server
    server_task = asyncio.create_task(server.setup())
    explorer_task = asyncio.create_task(explorer.setup())

    await server_task
    await explorer_task

asyncio.run(main())