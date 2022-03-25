from typing import TypedDict

class TransactionType(TypedDict):
    hash: str
    sender: str
    receiver: str
    signature: str
    timestamp: int
    amount: int

class BlockType(TypedDict):
    mined_by: str
    transactions: list[TransactionType]
    height: int
    target: str
    hash: str
    previous_hash: str
    nonce: str
    timestamp: int


class PeerType(TypedDict):
    ip: str
    port: int
    last_seen: int


class PingType(TypedDict):
    block_height: int
    peer_count: int
    is_miner: bool