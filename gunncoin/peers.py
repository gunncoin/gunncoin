import asyncio
from gunncoin.blockchain import Blockchain
from gunncoin.connections import ConnectionPool
from explorer.explorer import Explorer

import structlog

from gunncoin.messages import (
    create_peers_message,
    create_block_message,
    create_transaction_message,
    create_ping_message,
)
from gunncoin.transactions import validate_transaction

logger = structlog.getLogger(__name__)


class P2PError(Exception):
    pass


class P2PProtocol:
    def __init__(self, server):
        from gunncoin.server import Server

        self.server: Server = server
        self.blockchain: Blockchain = server.blockchain
        self.connection_pool: ConnectionPool = server.connection_pool

    @staticmethod
    async def send_message(writer, message):
        writer.write(message.encode() + b"\n")

    async def handle_message(self, message, writer):
        message_handlers = {
            "block": self.handle_block,
            "ping": self.handle_ping,
            "peers": self.handle_peers,
            "transaction": self.handle_transaction,
        }

        handler = message_handlers.get(message["name"])
        if not handler:
            raise P2PError("Missing handler for message")

        await handler(message, writer)

    async def handle_ping(self, message, writer):
        """
        Executed when we receive a `ping` message
        """

        block_height = message["payload"]["block_height"]

        # If they're a miner, let's mark them as such
        writer.is_miner = message["payload"]["is_miner"]

        # Let's send our 20 most "alive" peers to this user
        peers = self.connection_pool.get_alive_peers(20)
        peer_address_list = []
        for peer in peers:
            peer_address_list.append({"ip": peer[1].address["ip"], "port": peer[1].address["port"]})
        peers_message = create_peers_message(
            self.server.external_ip, self.server.external_port, peer_address_list
        )
        await self.send_message(writer, peers_message)

        # Let's send them blocks if they have less than us
        if block_height < self.blockchain.last_block["height"]:
            # Send them each block in succession, from their height
            for block in self.blockchain.chain[block_height + 1 :]:
                await self.send_message(
                    writer,
                    create_block_message(
                        self.server.external_ip, self.server.external_port, block
                    ),
                )

    async def handle_transaction(self, message, writer):
        """
        Executed when we receive a transaction that was broadcast by a peer
        """
        logger.info("Received transaction")

        # Validate the transaction
        tx = message["payload"]

        if validate_transaction(tx) is True:
            # Add the tx to our pool, and propagate it to our peers
            if tx not in self.blockchain.pending_transactions:
                self.blockchain.pending_transactions.append(tx)

                for peer in self.connection_pool.get_alive_peers(20):
                    await self.send_message(
                        peer[1],
                        create_transaction_message(
                            self.server.external_ip, self.server.external_port, tx
                        ),
                    )
        else:
            logger.warning("Received invalid transaction")

    async def handle_block(self, message, writer):
        """
        Executed when we receive a block that was broadcast by a peer
        """
        logger.info(f"Received new block")

        block = message["payload"]
        if(not Blockchain.verify_block_hash(block)):
            logger.error("Block is invalid")
            return

        if(self.blockchain.has_block(block)):
            logger.info("Already have this block")
            return

        # Give the block to the blockain to append if valid
        self.blockchain.add_block(block)

        for transaction in block["transactions"]:
            self.blockchain.remove_transaction(transaction)
            # TODO: handle transactions in explorer dict

        # Transmit the block to our peers
        for peer in self.connection_pool.get_alive_peers(20):

            # Don't send it back to the guy who sent up the message
            if(ConnectionPool.compare_address(peer[0], writer)):
                continue

            await self.send_message(
                peer[1],
                create_block_message(
                    self.server.external_ip, self.server.external_port, block
                ),
            )

    async def handle_peers(self, message, writer):
        """
        Executed when we receive a list of peers that was broadcast by a peer
        """
        logger.info("Received new peers")

        peers = message["payload"]

        # Craft a ping message for us to send to each peer
        ping_message = create_ping_message(
            self.server.external_ip,
            self.server.external_port,
            len(self.blockchain.chain),
            len(self.connection_pool.get_alive_peers(50)),
            False,
        )

        logger.info(peers)

        for peer in peers:
            if (peer["ip"] == self.server.external_ip and 
                peer["port"] == self.server.external_port):
                continue

            # Create a connection and add them to our connection pool if successful
            reader, peer_writer = await asyncio.open_connection(peer["ip"], peer["port"])

            peer_address = peer.copy()
            peer_address.pop("last_seen")
            peer_writer.address = peer_address

            # We're only interested in the "writer"
            self.connection_pool.add_peer(peer_writer)

            # Send the peer a PING message
            await self.send_message(peer_writer, ping_message)