from __future__ import annotations

import heapq
import itertools
import random
from typing import List, Tuple

from eval.expected_utility import expected_utility_of_schedule
from eval.state_quality import Q, set_resource_weights
from models.schedule_state import ScheduleState
from models.transfer import TransferOperation
from models.transform import TransformOperation
from ops.transfer_engine import apply_transfer, IllegalOperation as TransferIllegal
from ops.transform_engine import apply_transform, IllegalOperation as TransformIllegal
from scheduler.output_writer import ScheduleWithScores, score_schedule, write_schedules
from scheduler.successors import generate_successors, participants_for_schedule
from utils.csv_loader import load_resource_weights, load_world_state
from utils.transform_parser import load_transform_templates_dir


class _OpApplicator:
    def __init__(self, templates):
        self.templates = templates

    def apply(self, world, op):
        try:
            if isinstance(op, TransferOperation):
                return apply_transfer(world, op)
            if isinstance(op, TransformOperation):
                return apply_transform(world, op, self.templates)
        except (TransferIllegal, TransformIllegal):
            return None
        return None


def _score_state(self_country: str, initial_world, state: ScheduleState, templates) -> float:
    participants = participants_for_schedule(self_country, state.schedule)
    result, _ = expected_utility_of_schedule(
        self_country=self_country,
        start_world=initial_world,
        schedule=state.schedule,
        participating_countries=participants,
        state_quality_fn=lambda w, c: Q(c, w),
        apply_op_fn=_OpApplicator(templates).apply,
    )
    if result is None:
        return float("-inf")
    return float(result.expected_utility)


def _trim_frontier(frontier, frontier_max_size: int):
    if frontier_max_size <= 0 or len(frontier) <= frontier_max_size:
        return frontier

    best_items = heapq.nsmallest(frontier_max_size, frontier)
    heapq.heapify(best_items)
    return best_items


def _country_resource_signature(world, country_name: str):
    country = world.get_country(country_name)

    items = []
    for resource_name, amount in sorted(country.resources.items()):
        if amount != 0:
            items.append((resource_name, amount))
    return tuple(items)

def country_scheduler(
    your_country_name,
    resources_filename,
    initial_state_filename,
    output_schedule_filename,
    num_output_schedules,
    depth_bound,
    frontier_max_size,
    templates_dir="data/templates/transforms",
    multiplier_cap=5,
    transfer_amount_cap=5,
    successor_keep_probability=0.7,
    random_seed=42,
):
    initial_world = load_world_state(initial_state_filename)
    weights = load_resource_weights(resources_filename)
    templates = load_transform_templates_dir(templates_dir)
    set_resource_weights(weights)

    rng = random.Random(random_seed)

    start = ScheduleState(world=initial_world, schedule=tuple(), depth=0)

    counter = itertools.count()
    frontier = []
    explored_best = {}

    complete_schedule_scores: List[Tuple[float, ScheduleState]] = []
    discovery_order_schedules: List[Tuple[float, ScheduleState]] = []

    # Stats
    states_expanded = 0
    schedules_generated = 0
    schedules_kept = 0
    complete_schedules = 0

    start_score = _score_state(
        self_country=your_country_name,
        initial_world=initial_world,
        state=start,
        templates=templates,
    )
    heapq.heappush(frontier, (-start_score, next(counter), start))

    while frontier:
        neg_priority, _, current_state = heapq.heappop(frontier)
        current_priority = -neg_priority

        states_expanded += 1

        schedule_key = tuple(map(str, current_state.schedule))
        best_seen = explored_best.get(schedule_key)
        if best_seen is not None and current_priority < best_seen:
            continue
        explored_best[schedule_key] = current_priority

        # Keep any non-empty schedule as a candidate output.
        if 0 < current_state.depth <= depth_bound:
            discovery_order_schedules.append((current_priority, current_state))

        # Count schedules that actually reach the depth bound as complete.
        if current_state.depth == depth_bound:
            complete_schedule_scores.append((current_priority, current_state))
            complete_schedules += 1
            continue

        successors = generate_successors(
            state=current_state,
            self_country=your_country_name,
            templates=templates,
            depth_bound=depth_bound,
            multiplier_cap=multiplier_cap,
            amount_cap=transfer_amount_cap,
        )

        schedules_generated += len(successors)

        kept_successors = []
        for successor in successors:
            if rng.random() <= successor_keep_probability:
                kept_successors.append(successor)

        if not kept_successors and successors:
            kept_successors = [rng.choice(successors)]

        schedules_kept += len(kept_successors)

        for successor in kept_successors:
            score = _score_state(
                self_country=your_country_name,
                initial_world=initial_world,
                state=successor,
                templates=templates,
            )
            if score == float("-inf"):
                continue

            heapq.heappush(frontier, (-score, next(counter), successor))

        frontier = _trim_frontier(frontier, frontier_max_size)

    # Deduplicate in discovery order.
    seen_signatures = set()
    top_complete_states = []

    for score, state in discovery_order_schedules:
        signature = _country_resource_signature(state.world, your_country_name)

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)
        top_complete_states.append(state)

        if len(top_complete_states) >= num_output_schedules:
            break

    scored_schedules: List[ScheduleWithScores] = []
    for state in top_complete_states:
        scored = score_schedule(
            self_country=your_country_name,
            start_world=initial_world,
            schedule=state.schedule,
            templates=templates,
        )
        if scored is not None:
            scored_schedules.append(scored)

    write_schedules(output_schedule_filename, scored_schedules)

    print("\n--- Scheduler Stats ---")
    print(f"Depth bound: {depth_bound}")
    print(f"States expanded: {states_expanded}")
    print(f"Schedules generated: {schedules_generated}")
    print(f"Schedules kept after pruning: {schedules_kept}")
    print(f"Complete schedules found: {complete_schedules}")
    print(f"Candidate schedules recorded: {len(discovery_order_schedules)}")
    print("-----------------------\n")

    return {
        "initial_world": initial_world,
        "weights": weights,
        "templates": templates,
        "top_schedules": scored_schedules,
        "schedule_discovery_order_eus": [score for score, _ in discovery_order_schedules],
        "states_expanded": states_expanded,
        "schedules_generated": schedules_generated,
        "schedules_kept": schedules_kept,
        "complete_schedules_found": complete_schedules,
    }

# def country_scheduler(
#     your_country_name,
#     resources_filename,
#     initial_state_filename,
#     output_schedule_filename,
#     num_output_schedules,
#     depth_bound,
#     frontier_max_size,
#     templates_dir="data/templates/transforms",
#     multiplier_cap=5,
#     transfer_amount_cap=5,
#     successor_keep_probability=0.7,
#     random_seed=42,
# ):
#     initial_world = load_world_state(initial_state_filename)
#     weights = load_resource_weights(resources_filename)
#     templates = load_transform_templates_dir(templates_dir)
#     set_resource_weights(weights)

#     rng = random.Random(random_seed)

#     start = ScheduleState(world=initial_world, schedule=tuple(), depth=0)

#     counter = itertools.count()
#     frontier = []
#     explored_best = {}

#     complete_schedule_scores: List[Tuple[float, ScheduleState]] = []
#     discovery_order_schedules: List[Tuple[float, ScheduleState]] = []

#     start_score = _score_state(
#         self_country=your_country_name,
#         initial_world=initial_world,
#         state=start,
#         templates=templates,
#     )
#     heapq.heappush(frontier, (-start_score, next(counter), start))

#     while frontier:
#         neg_priority, _, current_state = heapq.heappop(frontier)
#         current_priority = -neg_priority

#         schedule_key = tuple(map(str, current_state.schedule))
#         best_seen = explored_best.get(schedule_key)
#         if best_seen is not None and current_priority < best_seen:
#             continue
#         explored_best[schedule_key] = current_priority

#         # Any non-empty schedule up to the depth bound can be a candidate output.
#         if 0 < current_state.depth <= depth_bound:
#             complete_schedule_scores.append((current_priority, current_state))
#             discovery_order_schedules.append((current_priority, current_state))

#         # Stop expanding once we hit the maximum allowed depth.
#         if current_state.depth >= depth_bound:
#             continue

#         successors = generate_successors(
#             state=current_state,
#             self_country=your_country_name,
#             templates=templates,
#             depth_bound=depth_bound,
#             multiplier_cap=multiplier_cap,
#             amount_cap=transfer_amount_cap,
#         )

#         kept_successors = []
#         for successor in successors:
#             if rng.random() <= successor_keep_probability:
#                 kept_successors.append(successor)

#         if not kept_successors and successors:
#             kept_successors = [rng.choice(successors)]

#         for successor in kept_successors:
#             score = _score_state(
#                 self_country=your_country_name,
#                 initial_world=initial_world,
#                 state=successor,
#                 templates=templates,
#             )
#             if score == float("-inf"):
#                 continue

#             heapq.heappush(frontier, (-score, next(counter), successor))

#         frontier = _trim_frontier(frontier, frontier_max_size)

#     # Deduplicate in discovery order.
#     seen_signatures = set()
#     top_complete_states = []

#     for score, state in discovery_order_schedules:
#         signature = _country_resource_signature(state.world, your_country_name)

#         if signature in seen_signatures:
#             continue

#         seen_signatures.add(signature)
#         top_complete_states.append(state)

#         if len(top_complete_states) >= num_output_schedules:
#             break

#     scored_schedules: List[ScheduleWithScores] = []
#     for state in top_complete_states:
#         scored = score_schedule(
#             self_country=your_country_name,
#             start_world=initial_world,
#             schedule=state.schedule,
#             templates=templates,
#         )
#         if scored is not None:
#             scored_schedules.append(scored)

#     write_schedules(output_schedule_filename, scored_schedules)

#     return {
#         "initial_world": initial_world,
#         "weights": weights,
#         "templates": templates,
#         "top_schedules": scored_schedules,
#         "schedule_discovery_order_eus": [score for score, _ in discovery_order_schedules],
#     }