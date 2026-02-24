from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TransformTemplate:

    name: str
    inputs: Dict[str, int]
    outputs: Dict[str, int]


@dataclass(frozen=True)
class TransformOperation:
    country: str
    template_name: str
    multiplier: int = 1
