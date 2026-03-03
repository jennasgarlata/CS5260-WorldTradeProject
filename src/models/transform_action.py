from typing import Dict
from models.transform import TransformOperation, TransformTemplate
from models.schedule_state import ScheduleState
from ops.transform_engine import apply_transform, IllegalOperation

class TransformAction:
    ACTION_COST = 1.0

    def __init__(self, op: TransformOperation, templates: Dict[str, TransformTemplate], max_depth: int):
        self.op = op
        self.templates = templates
        self.max_depth = max_depth

    def apply(self, state: ScheduleState):
        if state.depth >= self.max_depth:
            return None

        try:
            new_world = apply_transform(state.world, self.op, self.templates)
        except IllegalOperation:
            return None

        return ScheduleState(
            world=new_world,
            schedule=state.schedule + (self.op,),
            depth=state.depth + 1
        )