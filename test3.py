
from gunncoin.blockchain import Blockchain
import structlog

logger = structlog.getLogger()
bc = Blockchain()

payload = [{"mined_by": "0", "height": 0, "transactions": [], "previous_hash": "0", "nonce": "0", "target": "0", "timestamp": 0, "hash": "b38cece72b27c2123fbb235c7e7f00f606fbea48d8b8334daeb00ad3e5a167d4"}, {"mined_by": "0", "transactions": [], "height": 0, "target": "0", "hash": "b38cece72b27c2123fbb235c7e7f00f606fbea48d8b8334daeb00ad3e5a167d4", "previous_hash": "0", "nonce": "0", "timestamp": 0}, {"mined_by": "8389437903df537bfa58f9fd767d191cefab3907b07491cb4e382b0f8b19824d", "height": 2, "transactions": [{"sender": "0", "receiver": "8389437903df537bfa58f9fd767d191cefab3907b07491cb4e382b0f8b19824d", "amount": 1, "timestamp": 1648234935, "signature": ""}], "previous_hash": "b38cece72b27c2123fbb235c7e7f00f606fbea48d8b8334daeb00ad3e5a167d4", "nonce": "d18d68bcd8fcbe11", "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "timestamp": 1648234937, "hash": "00000d264432196141fb1a9ac15a38f736200eb626729aa7b726161c6dfd5e1c"}]
for block in payload:
    bc.add_block(block)

del bc.chain[1:]
logger.info(bc.chain)
