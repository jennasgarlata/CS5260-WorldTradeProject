from __future__ import annotations

from typing import Callable, Iterable, Any, Dict
import math

WorldT = Any
OperationT = Any

from eval.reward import discounted_reward


def logistic_probability(
    x: float,
    L: float = 1.0,
    k: float = 1.0,
    x0: float = 0.0,
) -> float:
    """
    Logistic function:
        L / (1 + e^(-k(x - x0)))

    In project:
        L = 1
        x = DR(ci, sj)
    """
    return L / (1.0 + math.exp(-k * (x - x0)))


def country_accept_probability(
    *,
    country: str,
    start_world: WorldT,
    end_world: WorldT,
    n_steps: int,
    gamma: float,
    state_quality_fn: Callable,
    k: float = 1.0,
    x0: float = 0.0,
) -> float:
    """
    Computes P(ci, sj)

    x = DR(ci, sj)
    P = logistic(x)
    """

    dr = discounted_reward(
        country=country,
        start_world=start_world,
        end_world=end_world,
        n_steps=n_steps,
        gamma=gamma,
        state_quality_fn=state_quality_fn,
    )

    return logistic_probability(dr, L=1.0, k=k, x0=x0)


def schedule_success_probability(
    *,
    countries: Iterable[str],
    start_world: WorldT,
    end_world: WorldT,
    n_steps: int,
    gamma: float,
    state_quality_fn: Callable,
    k: float = 1.0,
    x0: float = 0.0,
) -> float:
    """
    P(sj) = product of P(ci, sj)
    """

    prob = 1.0

    for country in countries:
        p_ci = country_accept_probability(
            country=country,
            start_world=start_world,
            end_world=end_world,
            n_steps=n_steps,
            gamma=gamma,
            state_quality_fn=state_quality_fn,
            k=k,
            x0=x0,
        )
        prob *= p_ci

    return prob