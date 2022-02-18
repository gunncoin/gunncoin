import asyncio
from asyncio import StreamReader, StreamWriter
from gunncoin.peers import P2PProtocol
from gunncoin.transactions import block_reward_transaction

import structlog
from marshmallow.exceptions import MarshmallowError

from gunncoin.messages import BaseSchema, create_block_message, create_peers_message, create_ping_message
from gunncoin.utils import get_external_ip

logger = structlog.getLogger()  # <7>


class Server:
    def __init__(self, blockchain, connection_pool, p2p_protocol):
        self.blockchain = blockchain  # <1>
        self.connection_pool = connection_pool
        self.p2p_protocol = p2p_protocol(self)
        self.external_ip = "127.0.0.1"
        self.external_port = None

        if not (blockchain and connection_pool and p2p_protocol):
            logger.error(
                "'blockchain', 'connection_pool', and 'p2p_protocol' must all be instantiated"
            )
            raise Exception("Could not start")

    async def get_external_ip(self):
        self.external_ip = await get_external_ip()  # <2>

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        logger.info("got a new connection")
        logger.info(self.connection_pool.get_alive_peers(10))
        while True:
            try:
                # Wait forever on new data to arrive
                data = await reader.readuntil(b"\n")  # <3>
                decoded_data = data.decode("utf8").strip()  # <4>

                logger.info("Elmo got mail!")
                logger.info(decoded_data)

                try:
                    message = BaseSchema().loads(decoded_data)  # <5>
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
            logger.info("TODO: Check hard coded nodes (discovery protocol), checking my local pc 10.0.0.130 for now")
            
            # Open a connection with a known node on the network
            #reader, writer = await asyncio.open_connection("10.0.0.130", 8888)
            reader, writer = await asyncio.open_connection("127.0.0.1", 8887)

            # send them a ping message so that they give us an update
            ping_message = create_ping_message(self.external_ip, self.external_port, 0, 0, True)
            await P2PProtocol.send_message(writer, ping_message)

            # manually listen for connections
            logger.info("manually listening for incoming messages")
            await self.handle_connection(reader, writer)
        except (asyncio.exceptions.IncompleteReadError, ConnectionError) as e:
                # An error happened, break out of the wait loop
                logger.error("Failed to connect to the network")
                logger.error(e)

    async def listen(self, hostname="0.0.0.0", port=8888):
        server = await asyncio.start_server(self.handle_connection, hostname, port)
        logger.info(f"Server listening on {hostname}:{port}")

        self.external_port = port
        #await self.get_external_ip()
        logger.warning("using local ip")
        self.external_ip = "127.0.0.1"

        async with server:
            await server.serve_forever()

    async def start_mining(self, public_key: str):
        count = 0
        while True:
            try:
                # reward ourselves for when we solve the block
                reward_transaction = block_reward_transaction(public_key)
                self.blockchain.pending_transactions.append(reward_transaction)
                await self.blockchain.mine_new_block()

                block_message = create_block_message(self.external_ip, self.external_port, self.blockchain.chain[-1])
                for peer in self.connection_pool.get_alive_peers(20):
                    await P2PProtocol.send_message(
                        peer[1],
                        block_message,
                    )

                await asyncio.sleep(0)
                count += 1
                if count > 3:
                    break
            except Exception as e:
                logger.error(e)
                break