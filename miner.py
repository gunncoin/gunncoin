import sys
import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.server import Server

import structlog
logger = structlog.getLogger()

"""
We setup the networking in 3 possible ways:
- Check for UPNP: if it works, port forward the right port and we're good
- Tell the user to manually configure port forwarding on firewall
- TODO: Try nat punchthrough. This is hard?
"""

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool)

async def main():
    miner_address = ""
    with open("address.txt") as f:
        miner_address = f.readline()

    if miner_address == "":
        logger.error("no valid miner address")
        return

    logger.info("Mining address: " + miner_address)

    # Start the server
    await server.setup()
    await server.start_mining(public_address=miner_address)
    

asyncio.run(main())