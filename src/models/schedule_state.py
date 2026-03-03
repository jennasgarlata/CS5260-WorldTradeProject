from dataclasses import dataclass
from typing import Tuple, Any
from models.transform import TransformOperation
from models.world_state import WorldState

@dataclass(frozen=True)
class ScheduleState:
    world: WorldState
    schedule: Tuple[Any, ...]   # can store TransformOperation or TransferOperation
    depth: int