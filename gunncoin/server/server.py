import asyncio
from asyncio import StreamReader, StreamWriter
from random import choice
from gunncoin.blockchain import Blockchain
from gunncoin.server.connections import ConnectionPool
from gunncoin.server.peers import P2PProtocol
from gunncoin.transactions import block_reward_transaction
from gunncoin.util.trusted_nodes import TrustedNodes
from gunncoin.util.constants import NODE_PORT, CONFIG_PORT

import structlog
from marshmallow.exceptions import MarshmallowError

from gunncoin.server.messages import BaseSchema, create_block_message, create_peers_message, create_ping_message
from gunncoin.util.utils import get_external_ip

logger = structlog.getLogger()  # <7>


class Server:
    def __init__(self, blockchain: Blockchain, connection_pool: ConnectionPool):
        self.blockchain = blockchain  # <1>
        self.connection_pool = connection_pool
        self.p2p_protocol = P2PProtocol(self)
        self.external_ip = "127.0.0.1"
        self.external_port = NODE_PORT

        if not (blockchain and connection_pool):
            logger.error(
                "'blockchain' and 'connection_pool' must all be instantiated"
            )
            raise Exception("Could not start")

    async def get_external_ip(self):
        self.external_ip = await get_external_ip()  # <2>

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        logger.info("got a new connection")
        while True:
            try:
                # Wait forever on new data to arrive
                data = await reader.readuntil(b"\n")
                decoded_data = data.decode("utf8").strip()

                logger.info(decoded_data)

                try:
                    message = BaseSchema().loads(decoded_data)
                except MarshmallowError:
                    logger.info("Received unreadable message", peer=writer)
                    break

                # Extract the address from the message, add it to the writer object
                writer.address = message["meta"]["address"]

                # Let's add the peer to our connection pool
                self.connection_pool.add_peer(writer)

                # ...and handle the message
                await self.p2p_protocol.handle_message(message["message"], writer)  # <6>
                await writer.drain()

                if writer.is_closing():
                    break

            except (asyncio.exceptions.IncompleteReadError, ConnectionError) as e:
                # An error happened, break out of the wait loop
                logger.error(e)
                break

        # The connection has closed. Let's clean up...
        writer.close()
        await writer.wait_closed()
        self.connection_pool.remove_peer(writer)  # <7>

    async def connect_to_network(self):
        try:
            # Open a connection with a known node on the network
            trusted_node = TrustedNodes.get_random_node()
            logger.info(f"Discovery Protocol: {trusted_node}")

            reader, writer = await asyncio.open_connection(trusted_node, NODE_PORT)

            # send them a ping message so that they give us an update
            ping_message = create_ping_message(self.external_ip, self.external_port, len(self.blockchain.chain), 0, True)
            await P2PProtocol.send_message(writer, ping_message)

            # manually listen for connections
            await self.handle_connection(reader, writer)
        except (asyncio.exceptions.IncompleteReadError, ConnectionError) as e:
                # An error happened, break out of the wait loop
                logger.error("Failed to connect to the network")
                logger.error(e)

    async def listen(self, hostname="0.0.0.0"):
        server = await asyncio.start_server(self.handle_connection, hostname, self.external_port)
        logger.info(f"Server listening on port {self.external_port}")

        async with server:
            await server.serve_forever()

    async def setup(self):
        await self.get_external_ip()

        listen_task = asyncio.create_task(self.listen())
        connect_task = asyncio.create_task(self.connect_to_network())
        
        await listen_task
        await connect_task

    async def start_mining(self, public_address):
        mine_task = asyncio.create_task(self.mine_forever(public_address))
        await mine_task

    async def mine_forever(self, public_address: str):
        """
        Mine for a bit
        Get conflicting block
        send conflicting block from our miner
        get response
        """
        logger.info("START MINING")
        #await self.blockchain.make_conflicting_block(4)
        #block_message = create_block_message("127.0.0.1", 8888, {"mined_by": "", "height": 4, "transactions": [], "previous_hash": "000021a8846415d729d408067d5bfc010a4e1e14ee0965f7263dcdb1c0831806", "nonce": "d4a9ca18fd731fa0", "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "timestamp": 1646776288, "hash": "00004a56ba084ab01c628d9494fd118cf00cf14bda16c5cf4959b68fd35c85f4"})
        #await self.p2p_protocol.send_to_peers(block_message)
        #return
        
        while True:
            try:
                # reward ourselves for when we solve the block
                reward_transaction = block_reward_transaction(public_address)
                self.blockchain.pending_transactions.append(reward_transaction)
                await self.blockchain.mine_new_block(public_address=public_address)

                block_message = create_block_message(self.external_ip, self.external_port, self.blockchain.chain[-1])
                for peer in self.connection_pool.get_alive_peers(20):
                    await P2PProtocol.send_message(
                        peer[1],
                        block_message,
                    )

                await asyncio.sleep(0.5) # TODO: Remove and increase difficulty
            except Exception as e:
                logger.error(e)
                break