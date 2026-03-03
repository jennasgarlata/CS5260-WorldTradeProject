# src/models/transfer_action.py

from typing import Optional

from models.schedule_state import ScheduleState
from models.transfer import TransferOperation
from ops.transfer_engine import apply_transfer, IllegalOperation


class TransferAction:
    ACTION_COST = 1.0

    def __init__(self, op: TransferOperation, max_depth: int):
        self.op = op
        self.max_depth = max_depth

    def apply(self, state: ScheduleState) -> Optional[ScheduleState]:
        if state.depth >= self.max_depth:
            return None

        try:
            new_world = apply_transfer(state.world, self.op)
        except IllegalOperation:
            return None

        return ScheduleState(
            world=new_world,
            schedule=state.schedule + (self.op,),
            depth=state.depth + 1
        )
  