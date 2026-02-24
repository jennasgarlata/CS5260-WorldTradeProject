# src/models/transfer.py
from dataclasses import dataclass


@dataclass(frozen=True)
class TransferOperation:
    sender: str
    receiver: str
    resource: str
    amount: int
