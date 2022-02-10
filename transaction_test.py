from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

# Generate a new random signing key
signing_key = SigningKey.generate()

# Sign a message with the signing key
signed_hex = signing_key.sign(b"Attack at Dawn", encoder=HexEncoder)

# Obtain the verify key for a given signing key
verify_key = signing_key.verify_key

# Serialize the verify key to send it to a third party
verify_key_hex = verify_key.encode(encoder=HexEncoder)

# Create a VerifyKey object from a hex serialized public key
verify_key = VerifyKey(verify_key_hex, encoder=HexEncoder)

# Check the validity of a message's signature
# The message and the signature can either be passed together, or
# separately if the signature is decoded to raw bytes.
# These are equivalent:
verify_key.verify(signed_hex, encoder=HexEncoder)
signature_bytes = HexEncoder.decode(signed_hex.signature)
verify_key.verify(signed_hex.message, signature_bytes,
                  encoder=HexEncoder)

# Alter the signed message text
forged = signed_hex[:-1] + bytes([int(signed_hex[-1]) ^ 1])
# Will raise nacl.exceptions.BadSignatureError, since the signature check
# is failing
verify_key.verify(forged)