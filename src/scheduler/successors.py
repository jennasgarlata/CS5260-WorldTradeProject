from __future__ import annotations

from typing import Iterable, List, Sequence, Set

from models.schedule_state import ScheduleState
from models.transfer import TransferOperation
from models.transform import TransformOperation
from ops.transfer_engine import apply_transfer, IllegalOperation as TransferIllegal
from ops.transform_engine import apply_transform, IllegalOperation as TransformIllegal

# Keep the branching factor sane. These are easy to justify in your report/presentation.
DEFAULT_FORBIDDEN_TRANSFER_RESOURCES: Set[str] = {
    "Population",
    "Housing",
    "AvailableLand",
    "Water",
    "PotentialEnergyUsable",
}


def participants_for_schedule(self_country: str, schedule: Sequence[object]) -> Set[str]:
    participants = {self_country}
    for op in schedule:
        if hasattr(op, "sender") and hasattr(op, "receiver"):
            participants.add(op.sender)
            participants.add(op.receiver)
        elif hasattr(op, "country"):
            participants.add(op.country)
    return participants



def _legal_transform_successors(
    state: ScheduleState,
    self_country: str,
    templates,
    depth_bound: int,
    multiplier_cap: int,
) -> List[ScheduleState]:
    if state.depth >= depth_bound:
        return []

    next_states: List[ScheduleState] = []

    for template_name in templates.keys():
        for multiplier in range(1, multiplier_cap + 1):
            op = TransformOperation(
                country=self_country,
                template_name=template_name,
                multiplier=multiplier,
            )
            try:
                next_world = apply_transform(state.world, op, templates)
            except TransformIllegal:
                continue

            next_states.append(
                ScheduleState(
                    world=next_world,
                    schedule=state.schedule + (op,),
                    depth=state.depth + 1,
                )
            )

    return next_states



def _legal_transfer_successors(
    state: ScheduleState,
    self_country: str,
    depth_bound: int,
    amount_cap: int,
    forbidden_resources: Set[str],
) -> List[ScheduleState]:
    if state.depth >= depth_bound:
        return []

    next_states: List[ScheduleState] = []
    countries = list(state.world.countries.keys())

    for sender in countries:
        for receiver in countries:
            if sender == receiver:
                continue
            if self_country not in (sender, receiver):
                continue

            sender_country = state.world.get_country(sender)
            for resource_name, amount in sender_country.resources.items():
                have = int(amount)
                if have <= 0 or resource_name in forbidden_resources:
                    continue

                for transfer_amount in range(1, min(amount_cap, have) + 1):
                    op = TransferOperation(
                        sender=sender,
                        receiver=receiver,
                        resource=resource_name,
                        amount=transfer_amount,
                    )
                    try:
                        next_world = apply_transfer(state.world, op)
                    except TransferIllegal:
                        continue

                    next_states.append(
                        ScheduleState(
                            world=next_world,
                            schedule=state.schedule + (op,),
                            depth=state.depth + 1,
                        )
                    )

    return next_states



def generate_successors(
    state: ScheduleState,
    self_country: str,
    templates,
    depth_bound: int,
    multiplier_cap: int = 5,
    amount_cap: int = 5,
    forbidden_transfer_resources: Set[str] | None = None,
) -> List[ScheduleState]:
    forbidden = (
        forbidden_transfer_resources
        if forbidden_transfer_resources is not None
        else DEFAULT_FORBIDDEN_TRANSFER_RESOURCES
    )

    successors: List[ScheduleState] = []
    successors.extend(
        _legal_transform_successors(
            state=state,
            self_country=self_country,
            templates=templates,
            depth_bound=depth_bound,
            multiplier_cap=multiplier_cap,
        )
    )
    successors.extend(
        _legal_transfer_successors(
            state=state,
            self_country=self_country,
            depth_bound=depth_bound,
            amount_cap=amount_cap,
            forbidden_resources=forbidden,
        )
    )
    return successors