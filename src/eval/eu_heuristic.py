from eval.expected_utility import expected_utility_of_schedule
from eval.state_quality import Q

from models.transfer import TransferOperation
from models.transform import TransformOperation

from ops.transfer_engine import apply_transfer, IllegalOperation as TransferIllegal
from ops.transform_engine import apply_transform, IllegalOperation as TransformIllegal


class EUHeuristic:

    def __init__(self, self_country, initial_world, templates, gamma=0.9, failure_cost=-5.0):
        self.self_country = self_country
        self.initial_world = initial_world
        self.templates = templates          
        self.gamma = gamma
        self.failure_cost = failure_cost

    def _apply_op(self, world, op):
        try:
            if isinstance(op, TransferOperation):
                return apply_transfer(world, op)
            if isinstance(op, TransformOperation):
                return apply_transform(world, op, self.templates)  
            return None
        except (TransferIllegal, TransformIllegal):
            return None

    def apply(self, state):
        schedule = state.schedule
        participants = {self.self_country}
        for op in schedule:
            # TransferOperation has sender/receiver
            if hasattr(op, "sender") and hasattr(op, "receiver"):
                participants.add(op.sender)
                participants.add(op.receiver)
            # TransformOperation has country
            elif hasattr(op, "country"):
                participants.add(op.country)

        result, _ = expected_utility_of_schedule(
            self_country=self.self_country,
            start_world=self.initial_world,
            schedule=schedule,
            participating_countries=participants,
            state_quality_fn=lambda w, c: Q(c, w),
            apply_op_fn=self._apply_op,
            gamma=self.gamma,
            failure_cost=self.failure_cost,
        )

        if result is None:
            return float("-inf")

        return float(result.expected_utility)