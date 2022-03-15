import sys
import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.config.config import Config
from gunncoin.server.connections import ConnectionPool
from gunncoin.server.server import Server

import structlog
logger = structlog.getLogger()

"""
We setup the networking in 3 possible ways:
- Check for UPNP: if it works, port forward the right port and we're good
- Tell the user to manually configure port forwarding on firewall
- TODO: Try nat punchthrough. This is hard?

To install...
pyinstaller --onefile miner.py --hidden-import=_cffi_backend
"""

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool)
config = Config(server)

async def main():
    # Start the server
    server_task = asyncio.create_task(server.setup())
    config_task = asyncio.create_task(config.setup())

    await server_task
    await config_task
    

asyncio.run(main())