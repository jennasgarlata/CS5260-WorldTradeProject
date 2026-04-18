from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from eval.state_quality import Q
from eval.expected_utility import expected_utility_of_schedule
from models.transfer import TransferOperation
from models.transform import TransformOperation
from ops.transfer_engine import apply_transfer, IllegalOperation as TransferIllegal
from ops.transform_engine import apply_transform, IllegalOperation as TransformIllegal
from scheduler.successors import participants_for_schedule


@dataclass(frozen=True)
class ScheduleWithScores:
    schedule: Sequence[object]
    intermediate_eus: Sequence[float]
    final_eu: float


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



def score_schedule(self_country: str, start_world, schedule: Sequence[object], templates) -> ScheduleWithScores | None:
    applicator = _OpApplicator(templates)
    prefix_schedule: List[object] = []
    intermediate_eus: List[float] = []

    for op in schedule:
        prefix_schedule.append(op)
        participants = participants_for_schedule(self_country, prefix_schedule)
        result, _ = expected_utility_of_schedule(
            self_country=self_country,
            start_world=start_world,
            schedule=prefix_schedule,
            participating_countries=participants,
            state_quality_fn=lambda w, c: Q(c, w),
            apply_op_fn=applicator.apply,
        )
        if result is None:
            return None
        intermediate_eus.append(float(result.expected_utility))

    final_eu = intermediate_eus[-1] if intermediate_eus else 0.0
    return ScheduleWithScores(
        schedule=tuple(schedule),
        intermediate_eus=tuple(intermediate_eus),
        final_eu=final_eu,
    )



def write_schedules(output_schedule_filename: str, schedules: Sequence[ScheduleWithScores]) -> None:
    with open(output_schedule_filename, "w", encoding="utf-8") as f:
        for index, item in enumerate(schedules, start=1):
            f.write(f"Schedule {index} | Final EU: {item.final_eu:.6f}\n")
            f.write("[\n")
            for op, eu in zip(item.schedule, item.intermediate_eus):
                f.write(f"{op} EU: {eu:.6f}\n")
            f.write("]\n\n")
