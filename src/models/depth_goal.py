from models.schedule_state import ScheduleState

class DepthGoal:
    def __init__(self, max_depth: int):
        self.max_depth = max_depth

    def __eq__(self, other) -> bool:
        return isinstance(other, ScheduleState) and other.depth >= self.max_depth
    