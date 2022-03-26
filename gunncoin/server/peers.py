import asyncio
from gunncoin.blockchain import Blockchain, BlockchainError
from gunncoin.server.connections import ConnectionPool
from gunncoin.explorer.messages import BalanceResponse, create_balance_request
from gunncoin.server.types import BlockType

import structlog

from gunncoin.server.messages import (
    create_consensus_message,
    create_peers_message,
    create_block_message,
    create_transaction_message,
    create_ping_message,
)
from gunncoin.transactions import validate_transaction
from gunncoin.util.trusted_nodes import TrustedNodes

logger = structlog.getLogger(__name__)


class P2PError(Exception):
    pass


class P2PProtocol:
    def __init__(self, server):
        from gunncoin.server.server import Server

        self.server: Server = server
        self.blockchain: Blockchain = server.blockchain
        self.connection_pool: ConnectionPool = server.connection_pool

    @staticmethod
    async def send_message(writer, message):
        writer.write(message.encode() + b"\n")

    async def send_to_peers(self, message, ignore_writer=None):
        for peer in self.connection_pool.get_alive_peers(15):
            if ignore_writer and ConnectionPool.compare_address(peer[0], ignore_writer):
                continue

            await self.send_message(peer[1], message)

    async def handle_message(self, message, writer):
        message_handlers = {
            "block": self.handle_block,
            "ping": self.handle_ping,
            "peers": self.handle_peers,
            "transaction": self.handle_transaction,
            "consensus": self.handle_consensus,
        }

        handler = message_handlers.get(message["name"])
        if not handler:
            raise P2PError("Missing handler for message")

        await handler(message, writer)

    async def handle_ping(self, message, writer):
        """
        Executed when we receive a `ping` message
        """
        logger.info("Handle ping message")

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

        logger.info("Sent peers")

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
            logger.info("Sent blocks")
        elif block_height > self.blockchain.last_block["height"]:
            logger.warning("New peer has more blocks than us, blockchain will be overritten")
            # TODO: This is like broken or something idk, duplicate blocks
            await self.send_message(
                writer,
                create_consensus_message(
                    self.server.external_ip, self.server.external_port,
                    chain=self.blockchain.chain
                )
            )

    async def handle_transaction(self, message, writer):
        """
        Executed when we receive a transaction that was broadcast by a peer

        TODO: make a transaction pool, remove from pool when mined. or remove it when we see a block
        """
        logger.info("Received transaction")

        # Extract transaction
        tx = message["payload"]

        # Validate the transaction
        if validate_transaction(tx) is False:
            return

        if tx["amount"] > self.blockchain.check_balance(tx["sender"]):
            logger.warning("Insufficient funds")
            return


        # Add the tx to our pool, and propagate it to our peers
        if tx not in self.blockchain.pending_transactions:
            self.blockchain.pending_transactions.append(tx)     
            await self.send_to_peers(
                    create_transaction_message(
                        self.server.external_ip, self.server.external_port, tx
                    ),
                    ignore_writer=writer
                )

    async def handle_block(self, message, writer):
        """
        Executed when we receive a block that was broadcast by a peer
        """
        logger.info(f"Received new block")

        block = message["payload"]
        if(not Blockchain.verify_block(block)):
            logger.error("Block is invalid")
            return

        try:
            if(self.blockchain.has_block(block)):
                logger.info("Already have this block")
                return
        except BlockchainError as e:
            logger.warning(e)
            logger.info("Send them consensus message to resolve conflict")
            await self.send_message(writer, create_consensus_message(
                self.server.external_ip, self.server.external_port,
                chain=self.blockchain.chain
            ))
            return

        # Give the block to the blockain to append if valid
        self.blockchain.add_block(block)
        logger.info(f"Added block {block['height']}")

        for transaction in block["transactions"]:
            self.blockchain.remove_transaction(transaction)
            # TODO: handle transactions in explorer dict

        # Transmit the block to our peers, but not to the guy who sent use the message
        await self.send_to_peers(
            create_block_message(
                self.server.external_ip, self.server.external_port, block
            ), 
            ignore_writer=writer
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

    async def handle_consensus(self, message, writer):
        """
        We received a consensus request

        We likely sent them a block that they don't agree with, so they gave us their updated blocks
        We're getting all of their blocks because they think we are doing suspicious stuff...
        Blockchain forks probably won't happen! ...maybe... i hope....
        """

        logger.info("Received consensus request")
        new_blocks: list[BlockType] = message["payload"]["blocks"]
        logger.info("first couple blocks " + str(new_blocks[:3]))
        logger.info(new_blocks[-1]['height'])
        logger.info(self.blockchain.last_block['height'])

        if new_blocks[-1]["height"] < self.blockchain.last_block["height"]:
            logger.info("We have newer blocks than them, send them our blocks")
            await self.send_message(writer, create_consensus_message(
                self.server.external_ip, self.server.external_port,
                chain=self.blockchain.chain
            ))
            return

        # Check if the new blocks are valid
        if not Blockchain.validate_chain(new_blocks):
            logger.warning("Consensus payload contains invalid blocks")
            return

        # Check if new blocks will work with our local blockchain
        min_height = new_blocks[0]["height"]
        if new_blocks[0]["height"] > 0 and new_blocks[0]["previous_hash"] != self.blockchain.chain[min_height-1]["hash"]:
            logger.warning("New blocks won't fit in our blockchain, requesting new blocks")
            logger.info("TODO: request new blocks... If you see this, something bad happened and you should restart!") 
            # send request to miner ip/port
            return

        # Passed checks, so let's add the blocks to our chain
        self.blockchain.merge_blockchain(new_blocks)
        