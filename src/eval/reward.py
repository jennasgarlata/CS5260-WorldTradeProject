from __future__ import annotations

from eval.params import GAMMA
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Tuple, Any
import copy
import math

WorldT = Any          # your WorldState type
OperationT = Any      # TransferOperation / TransformOperation / Action wrapper type

StateQualityFn = Callable[[WorldT, str], float]
ApplyOpFn = Callable[[WorldT, OperationT], Optional[WorldT]]


@dataclass(frozen=True)
class RewardResult:
    country: str
    q_start: float
    q_end: float
    reward: float              # undiscounted reward
    discounted_reward: float   # discounted reward
    gamma: float
    n_steps: int


def _validate_gamma(gamma: float) -> None:
    if not (0.0 <= gamma < 1.0):
        raise ValueError(f"gamma must satisfy 0 <= gamma < 1, got {gamma}")


def _discount_factor(gamma: float, n_steps: int) -> float:
    _validate_gamma(GAMMA)
    if n_steps < 0:
        raise ValueError(f"n_steps must be >= 0, got {n_steps}")
    # gamma^N
    return float(gamma) ** int(n_steps)


def undiscounted_reward(
    *,
    country: str,
    start_world: WorldT,
    end_world: WorldT,
    state_quality_fn: StateQualityFn,
) -> float:
    """
    R(ci, sj) = Qend(ci, sj) - Qstart(ci, sj).
    """
    q_start = float(state_quality_fn(start_world, country))
    q_end = float(state_quality_fn(end_world, country))
    return q_end - q_start


def discounted_reward(
    *,
    country: str,
    start_world: WorldT,
    end_world: WorldT,
    n_steps: int,
    state_quality_fn: StateQualityFn,
) -> float:
    """
    DR(ci, sj) = gamma^N * (Qend - Qstart), 0 <= gamma < 1.
    Reward is assumed to come from the final state only.
    """
    r = undiscounted_reward(
        country=country,
        start_world=start_world,
        end_world=end_world,
        state_quality_fn=state_quality_fn,
    )
    return _discount_factor(GAMMA, n_steps) * r


def simulate_schedule(
    *,
    start_world: WorldT,
    schedule: Iterable[OperationT],
    apply_op_fn: ApplyOpFn,
    copy_world: bool = True,
) -> Optional[WorldT]:
    """
    Applies each operation in order; returns final world if all ops succeed.
    If any op is illegal/fails (apply_op_fn returns None), returns None.
    """
    world = copy.deepcopy(start_world) if copy_world else start_world

    for op in schedule:
        world2 = apply_op_fn(world, op)
        if world2 is None:
            return None
        world = world2

    return world


def rewards_from_schedule(
    *,
    country: str,
    start_world: WorldT,
    schedule: Iterable[OperationT],
    state_quality_fn: StateQualityFn,
    apply_op_fn: ApplyOpFn,
    copy_world: bool = True,
) -> Tuple[Optional[RewardResult], Optional[WorldT]]:
    """
    Simulate schedule, then compute both R and DR.

    We interpret N as the number of operators in the schedule (time steps).
    """
    _validate_gamma(GAMMA)
    schedule_list = list(schedule)
    n_steps = len(schedule_list)

    end_world = simulate_schedule(
        start_world=start_world,
        schedule=schedule_list,
        apply_op_fn=apply_op_fn,
        copy_world=copy_world,
    )
    if end_world is None:
        return None, None

    q_start = float(state_quality_fn(start_world, country))
    q_end = float(state_quality_fn(end_world, country))
    r = q_end - q_start
    dr = _discount_factor(GAMMA, n_steps) * r

    return (
        RewardResult(
            country=country,
            q_start=q_start,
            q_end=q_end,
            reward=r,
            discounted_reward=dr,
            gamma=float(GAMMA),
            n_steps=n_steps,
        ),
        end_world,
    )