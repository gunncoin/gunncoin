import asyncio
import requests
from explorer.explorer_messages import create_balance_request, create_transaction_request
from gunncoin.blockchain import Blockchain
from gunncoin.messages import PingMessage, create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.peers import P2PProtocol
from gunncoin.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from gunncoin import portforwardlib
from nacl.signing import SigningKey
import nacl
import structlog
 
logger = structlog.getLogger()
 
port = 8888
portforwardlib.forwardPort(port, port, None, None, False, "TCP", 0, "", True)
