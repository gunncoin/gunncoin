import json
from nacl.encoding import HexEncoder, Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey
import structlog
from gunncoin.transactions import validate_transaction

logger = structlog.getLogger()

signing_key = SigningKey.generate()

def create_transaction(
    private_key: str, public_key: str, receiver: str, amount: int
) -> dict:
    tx = {
        "sender": public_key,
        "receiver": receiver,
        "amount": amount,
        "timestamp": 1647737385,
    }
    tx_bytes = json.dumps(tx, sort_keys=True).encode("ascii")
    logger.info(tx_bytes.hex())

    # Generate a signing key from the private key
    signing_key = SigningKey(private_key, encoder=HexEncoder)

    logger.info(bytes(signing_key).hex())
    # Now add the signature to the original transaction
    signedMessage = signing_key.sign(tx_bytes)
    tx["signature"] = HexEncoder.encode(signedMessage.signature).decode("ascii")

    return tx

alice_private = "bf3f1a7e8911dc9fd0b50e829bb03a301775d0bee630865ad401791e77d21ddc"
alices_public = "034e06f1d959fe83fd3f65627b7e2e2d3c020f99cd99bcd3a4dd649e65e3a684"
bobs_private = "9ea1d7796f88ffc8d81e4a345b4dba2af2f2a081e0aa2e22e6b8475486a30baf"
bobs_public = "81acbfc871192f9d1abf4ca6c65b05b8530c62e27e622dad7aa7642560e4a53c"
transaction = create_transaction(alice_private, alices_public, bobs_public, 3)