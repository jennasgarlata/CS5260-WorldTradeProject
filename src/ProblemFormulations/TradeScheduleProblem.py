# from dataclasses import dataclass
# from typing import Dict, List, Tuple

# #from ProblemFormulations.Problem import Problem
# from models.world_state import WorldState
# from models.transform import TransformOperation, TransformTemplate
# from ops.transform_engine import apply_transform, IllegalOperation


# @dataclass(frozen=True)
# class ScheduleState:
#     world: WorldState
#     schedule: Tuple[object, ...]
#     depth: int


# class TradeScheduleProblem:

#     def __init__(
#         self,
#         initial_world: WorldState,
#         templates: Dict[str, TransformTemplate],
#         max_depth: int = 3,
#     ):
#         self.initial_world = initial_world
#         self.templates = templates
#         self.max_depth = max_depth

#     def initial_state(self) -> ScheduleState:
#         return ScheduleState(
#             world=self.initial_world,
#             schedule=tuple(),
#             depth=0,
#         )

#     def actions(self, state: ScheduleState) -> List[TransformOperation]:

#         if state.depth >= self.max_depth:
#             return []

#         world = state.world
#         actions = []

#         for country_name in world.countries.keys():
#             for template_name, template in self.templates.items():

#                 max_k = self._max_multiplier(world, country_name, template)

#                 # Try only a few multipliers to avoid explosion
#                 for k in [1, max_k]:
#                     if k < 1:
#                         continue

#                     op = TransformOperation(
#                         country=country_name,
#                         template_name=template_name,
#                         multiplier=k,
#                     )

#                     if self._can_apply(world, op):
#                         actions.append(op)

#         return actions

#     def result(self, state: ScheduleState, action: TransformOperation) -> ScheduleState:

#         new_world = apply_transform(state.world, action, self.templates)

#         return ScheduleState(
#             world=new_world,
#             schedule=state.schedule + (action,),
#             depth=state.depth + 1,
#         )

#     def step_cost(self, state, action, next_state):
#         return 1

#     def is_goal(self, state):
#         return False

#     # ----------------- helpers -----------------

#     def _can_apply(self, world, op):
#         try:
#             _ = apply_transform(world, op, self.templates)
#             return True
#         except IllegalOperation:
#             return False

#     def _max_multiplier(self, world, country_name, template):

#         country = world.get_country(country_name)
#         max_k = float("inf")

#         if not template.inputs:
#             return 1

#         for r, unit_amt in template.inputs.items():
#             if unit_amt <= 0:
#                 continue

#             have = country.get(r)
#             max_k = min(max_k, have // unit_amt)

#         if max_k == float("inf"):
#             return 1

#         return int(max_k)


from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ProblemFormulations.Problem import Problem
from models.world_state import WorldState
from models.transform import TransformOperation, TransformTemplate
from ops.transform_engine import apply_transform, IllegalOperation
from models.schedule_state import ScheduleState

class TradeScheduleProblem(Problem):

    def __init__(
        self,
        initial_world: WorldState,
        templates: Dict[str, TransformTemplate],
        max_depth: int = 3,
        heuristic: Optional[object] = None,
    ):
        # The professor framework requires (states, actions, heuristic)
        super().__init__(states=[], actions=[], heuristic=heuristic)

        self.initial_world = initial_world
        self.templates = templates
        self.max_depth = max_depth

        # Cache start state
        self._start = ScheduleState(world=initial_world, schedule=tuple(), depth=0)

    # ---- Provide BOTH naming styles so whichever the SearchStrategies expect will work ----

    # Style A (your earlier style)
    def initial_state(self) -> ScheduleState:
        return self._start

    def actions(self, state: ScheduleState) -> List[TransformOperation]:
        return self.getActions(state)

    def result(self, state: ScheduleState, action: TransformOperation) -> ScheduleState:
        return self.transition(state, action)

    def is_goal(self, state: ScheduleState) -> bool:
        return self.goalTest(state)

    # Style B (common professor search style)
    def getStartState(self) -> ScheduleState:
        return self._start

    def goalTest(self, state: ScheduleState) -> bool:
        # Part 1 is optimization under a depth horizon, not goal-reaching
        return False

    def getActions(self, state: ScheduleState) -> List[TransformOperation]:
        if state.depth >= self.max_depth:
            return []

        world = state.world
        actions: List[TransformOperation] = []

        for country_name in world.countries.keys():
            for template_name, template in self.templates.items():
                max_k = self._max_multiplier(world, country_name, template)

                # Try a small set of multipliers (keeps branching sane)
                for k in self._candidate_multipliers(max_k):
                    op = TransformOperation(country=country_name, template_name=template_name, multiplier=k)
                    if self._can_apply(world, op):
                        actions.append(op)

        return actions

    def transition(self, state: ScheduleState, action: TransformOperation) -> ScheduleState:
        new_world = apply_transform(state.world, action, self.templates)
        return ScheduleState(
            world=new_world,
            schedule=state.schedule + (action,),
            depth=state.depth + 1,
        )

    def stepCost(self, state: ScheduleState, action: TransformOperation, next_state: ScheduleState) -> float:
        return 1.0

    # ---- helpers ----

    def _can_apply(self, world: WorldState, op: TransformOperation) -> bool:
        try:
            _ = apply_transform(world, op, self.templates)
            return True
        except IllegalOperation:
            return False

    def _candidate_multipliers(self, max_k: int) -> List[int]:
        # Include max_k so you still get your big-transform option, but keep options limited
        candidates = {1, 2, 3, max_k}
        return sorted([k for k in candidates if 1 <= k <= max_k])

    def _max_multiplier(self, world: WorldState, country_name: str, template: TransformTemplate) -> int:
        c = world.get_country(country_name)

        if not template.inputs:
            return 1

        max_k = float("inf")
        for r, unit_amt in template.inputs.items():
            if unit_amt <= 0:
                continue
            have = c.get(r)
            max_k = min(max_k, have // unit_amt)

        return int(max_k) if max_k != float("inf") else 1