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
    if len(sys.argv) <= 1 or not sys.argv[1].isdigit():
        logger.error("please enter a valid port address")

    port = int(sys.argv[1])

    miner_address = ""
    with open("address.txt") as f:
        miner_address = f.readline()

    if miner_address == "":
        logger.error("no valid miner address")
        return

    logger.info("Mining address: " + miner_address)

    # Start the server
    listen_task = asyncio.create_task(server.listen(hostname="127.0.0.1", port=port))
    connect_task = asyncio.create_task(server.connect_to_network())
    mining_task = asyncio.create_task(server.start_mining(public_address=miner_address))

    await listen_task
    await connect_task
    await mining_task
    

asyncio.run(main())