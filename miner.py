import sys
import asyncio

from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from gunncoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

import structlog
logger = structlog.getLogger()

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