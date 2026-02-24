from typing import Dict

from models.transform import TransformOperation, TransformTemplate


class IllegalOperation(ValueError):
    """Raised when a TRANSFORM cannot be applied."""
    pass


def can_transform(country_resources: Dict[str, int],
                  template: TransformTemplate,
                  multiplier: int) -> bool:
    """
    Check whether country has enough inputs (scaled by multiplier).
    Missing resources count as 0.
    """
    if multiplier < 1:
        return False

    for resource, unit_amt in template.inputs.items():
        need = unit_amt * multiplier
        have = country_resources.get(resource, 0)
        if have < need:
            return False

    return True


def apply_transform(world_state,
                    op: TransformOperation,
                    templates: Dict[str, TransformTemplate]):
    """
    Applies TRANSFORM and returns a NEW world_state.
    Assumes:
      - world_state.countries is dict[str, Country]
      - Country has .resources dict[str,int]
      - WorldState and Country both have copy()
    """

    if op.template_name not in templates:
        raise IllegalOperation(f"Unknown template '{op.template_name}'")

    if op.country not in world_state.countries:
        raise IllegalOperation(f"Unknown country '{op.country}'")

    template = templates[op.template_name]
    m = op.multiplier

    # copy-on-write
    new_world = world_state.copy()
    country = new_world.countries[op.country].copy()
    resources = dict(country.resources)

    if not can_transform(resources, template, m):
        deficits = []
        for r, unit_amt in template.inputs.items():
            need = unit_amt * m
            have = resources.get(r, 0)
            if have < need:
                deficits.append(f"{r} need {need}, have {have}")
        raise IllegalOperation(
            f"TRANSFORM failed for {op.country} using {template.name}: "
            + ", ".join(deficits)
        )

    # subtract inputs
    for r, unit_amt in template.inputs.items():
        resources[r] = resources.get(r, 0) - (unit_amt * m)
        if resources[r] < 0:
            raise IllegalOperation(f"Resource '{r}' went negative")

    # add outputs
    for r, unit_amt in template.outputs.items():
        resources[r] = resources.get(r, 0) + (unit_amt * m)

    country.resources = resources
    new_world.countries[op.country] = country

    return new_world
