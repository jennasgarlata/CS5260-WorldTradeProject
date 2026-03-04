from __future__ import annotations

from eval.params import GAMMA, LOGISTIC_K, LOGISTIC_X0, FAILURE_COST
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Any, Dict, List, Set, Tuple

from eval.reward import simulate_schedule, discounted_reward
from eval.probability import schedule_success_probability

WorldT = Any
OperationT = Any
ApplyOpFn = Callable[[WorldT, OperationT], Optional[WorldT]]
StateQualityFn = Callable[[WorldT, str], float]


@dataclass(frozen=True)
class ExpectedUtilityResult:
    self_country: str
    n_steps: int
    gamma: float

    # probabilities
    p_schedule: float

    # rewards
    discounted_reward_self: float

    # failure cost
    failure_cost: float

    # expected utility
    expected_utility: float


def expected_utility_of_schedule(
    *,
    self_country: str,
    start_world: WorldT,
    schedule: Iterable[OperationT],
    participating_countries: Iterable[str],
    state_quality_fn: StateQualityFn,
    apply_op_fn: ApplyOpFn,
    # logistic parameters (start points per spec)
    # cost of failure C (negative constant per spec)
    copy_world: bool = True,
) -> Tuple[Optional[ExpectedUtilityResult], Optional[WorldT]]:
    """
    EU(self, sj) = (P(sj) * DR(self, sj)) + ((1 - P(sj)) * C)

    - P(sj) is product of individual acceptance probabilities
    - Each acceptance probability uses logistic with x = DR(ci, sj)
    - C is a negative constant (you choose/justify)

    Returns (result, end_world) or (None, None) if schedule is illegal (simulation fails).
    """

    # Make schedule concrete so we can count steps
    schedule_list = list(schedule)
    n_steps = len(schedule_list)

    # 1) simulate to get end world (illegal schedule -> None)
    end_world = simulate_schedule(
        start_world=start_world,
        schedule=schedule_list,
        apply_op_fn=apply_op_fn,
        copy_world=copy_world,
    )
    if end_world is None:
        return None, None

    # 2) discounted reward for self
    dr_self = discounted_reward(
        country=self_country,
        start_world=start_world,
        end_world=end_world,
        n_steps=n_steps,
        state_quality_fn=state_quality_fn,
    )

    # 3) schedule success probability over participating countries
    p_sj = schedule_success_probability(
        countries=participating_countries,
        start_world=start_world,
        end_world=end_world,
        n_steps=n_steps,
        state_quality_fn=state_quality_fn,
    )

    # 4) expected utility
    eu = (p_sj * dr_self) + ((1.0 - p_sj) * float(FAILURE_COST))

    return (
        ExpectedUtilityResult(
            self_country=self_country,
            n_steps=n_steps,
            gamma=float(GAMMA),
            p_schedule=float(p_sj),
            discounted_reward_self=float(dr_self),
            failure_cost=float(FAILURE_COST),
            expected_utility=float(eu),
        ),
        end_world,
    )