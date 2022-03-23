import asyncio
import requests
import socket
from gunncoin.blockchain import Blockchain
from gunncoin.config.messages import create_config_request
from gunncoin.server.messages import PingMessage, create_block_message, create_ping_message, BaseSchema, create_transaction_message
from gunncoin.server.peers import P2PProtocol
from gunncoin.server.schema import Block, Peer, Transaction
from gunncoin.transactions import create_transaction
from gunncoin.util.constants import CONFIG_PORT, NODE_PORT
from gunncoin.util.utils import get_local_ip
from nacl.signing import SigningKey
import nacl
import structlog
from gunncoin.util.trusted_nodes import TrustedNodes

logger = structlog.getLogger()

"""
# Generate secret keys for Alice and Bob
alices_private_key = SigningKey.generate()
bobs_private_key = SigningKey.generate()
# Public keys are generated from the private keys
alices_public_key = alices_private_key.verify_key
bobs_public_key = bobs_private_key.verify_key

alice_private = bytes(alices_private_key).hex()
alices_public = bytes(alices_public_key).hex()

bobs_private = bytes(bobs_private_key).hex()
bobs_public = bytes(bobs_public_key).hex()
"""

alice_private = "bf3f1a7e8911dc9fd0b50e829bb03a301775d0bee630865ad401791e77d21ddc"
alices_public = "034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684"
bobs_private = "9ea1d7796f88ffc8d81e4a345b4dba2af2f2a081e0aa2e22e6b8475486a30baf"
bobs_public = "81acbfc871192f9d1abf4ca6c65b05b8530c62e27e622dad7aa7642560e4a53c"


transaction = create_transaction(alice_private, alices_public, bobs_public, 3)
transaction2 = create_transaction(alice_private, alices_public, bobs_public, 5)

tx_message = create_transaction_message("127.0.0.1", 88, transaction)
tx_message2 = create_transaction_message("127.0.0.1", 88, transaction2)

#req = create_transaction_request(transaction)
req = create_config_request(public_address="034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684", start_mining=True)

block_message =create_block_message("127.0.0.1", 8888, {"height": 5, "transactions": [], "previous_hash": "000079d51f00700cbefcb21da0f5f0ec19871d25628c449eb21ec49dffd482b3", "nonce": "248d3c540e8d3fe2", "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "timestamp": 1646683818, "hash": "00006388e837e95242569704499f169c3840055ad7a1fbf8f8354d9ee369901a"})
consensus_message = '{"meta": {"client": "gunncoin-0.1", "address": {"ip": "45.33.51.145", "port": 4866}}, "message": {"payload": {"blocks": [ {"transactions": [{"timestamp": 1646696521, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 1, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "000066dfb30e8d00001f28ea15a37d8a79ec5ead5a87c407dc7a57b48ca6628b", "previous_hash": "23dce3ba3d407f34fd0d99215e0fefe0e09a45e6df149fd449e20cf8a31e69b6", "nonce": "ce56600e66c53d28", "timestamp": 1646696522}, {"transactions": [{"timestamp": 1646696522, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 2, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "00003cac040e5f060b1ab748bce2041c5cba7973aeed65d66ae9477cb9c5c087", "previous_hash": "000066dfb30e8d00001f28ea15a37d8a79ec5ead5a87c407dc7a57b48ca6628b", "nonce": "3e0acc4beae9e95a", "timestamp": 1646696523}, {"transactions": [{"timestamp": 1646696524, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 3, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "000055ab3f0c622cfb99bb00d9aceffbfe6a2c57e74ef64c2219d9bd094d556b", "previous_hash": "00003cac040e5f060b1ab748bce2041c5cba7973aeed65d66ae9477cb9c5c087", "nonce": "3287ca18ae724179", "timestamp": 1646696524}, {"transactions": [{"timestamp": 1646696525, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 4, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "0000b3e76e45cc7605575f1af104d3072a821fa19a0cbdb8a1d5b0cb3338d2b6", "previous_hash": "000055ab3f0c622cfb99bb00d9aceffbfe6a2c57e74ef64c2219d9bd094d556b", "nonce": "1bd67a4798121ea4", "timestamp": 1646696526}, {"transactions": [{"timestamp": 1646696526, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 5, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "00006eb1fe815b4c6c163b8e69a4656b3edca8e1bb53f2d7365977985f726502", "previous_hash": "0000b3e76e45cc7605575f1af104d3072a821fa19a0cbdb8a1d5b0cb3338d2b6", "nonce": "a8dae6230ba4432f", "timestamp": 1646696526}, {"transactions": [{"timestamp": 1646696527, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 6, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "0000ce54fcc1b810756c689f3748f64c3b17e6f444a6e3033e617278bb0d1773", "previous_hash": "00006eb1fe815b4c6c163b8e69a4656b3edca8e1bb53f2d7365977985f726502", "nonce": "7d50f2b340012f27", "timestamp": 1646696527}, {"transactions": [{"timestamp": 1646696527, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 7, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "00005a8bbc6deeded3e099496fc4231fc913d73417676545d500e7ebc80f02ef", "previous_hash": "0000ce54fcc1b810756c689f3748f64c3b17e6f444a6e3033e617278bb0d1773", "nonce": "231632f6a567480f", "timestamp": 1646696530}, {"transactions": [{"timestamp": 1646696530, "sender": "0", "receiver": "0146e69feee8f0653a093b67aa8e22e31b5c6ba936fc324efdd835deb80e1838", "amount": 1, "signature": ""}], "height": 8, "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "hash": "0000fefed31195848d648fa3a48b8a8c0271ec0abf7139c51ac61fe336edea1a", "previous_hash": "00005a8bbc6deeded3e099496fc4231fc913d73417676545d500e7ebc80f02ef", "nonce": "1b67f34562421bac", "timestamp": 1646696533}]}, "name": "consensus"}}'
#BaseSchema().loads(consensus_message)

async def test():

    reader, writer = await asyncio.open_connection(TrustedNodes.get_random_node(), NODE_PORT)
    await P2PProtocol.send_message(writer, tx_message)
    data = await reader.readuntil(b"\n")  # <3>
    decoded_data = data.decode("utf8").strip()  # <4>

    logger.info(decoded_data)

asyncio.run(test())