from models.transfer import TransferOperation


class IllegalOperation(ValueError):
    """Raised when a TRANSFER cannot be applied."""
    pass


def can_transfer(world_state, op: TransferOperation) -> bool:
    """
    Checks legality of a transfer without changing state.
    Assumes:
      - world_state.countries is dict[str, Country]
      - Country has .resources dict[str,int]
    """
    if op.amount is None or op.amount <= 0:
        return False

    if op.sender not in world_state.countries:
        return False
    if op.receiver not in world_state.countries:
        return False

    sender_res = world_state.countries[op.sender].resources
    have = sender_res.get(op.resource, 0)

    return have >= op.amount


def apply_transfer(world_state, op: TransferOperation):
    """
    Applies TRANSFER and returns a NEW world_state.
    Copy-on-write:
      - copy the world
      - copy sender + receiver
      - update only those two
    """
    if not can_transfer(world_state, op):
        # Build a good error message for debugging
        sender_exists = op.sender in world_state.countries
        receiver_exists = op.receiver in world_state.countries

        if not sender_exists:
            raise IllegalOperation(f"TRANSFER failed: unknown sender '{op.sender}'")
        if not receiver_exists:
            raise IllegalOperation(f"TRANSFER failed: unknown receiver '{op.receiver}'")

        have = world_state.countries[op.sender].resources.get(op.resource, 0)
        raise IllegalOperation(
            f"TRANSFER failed: {op.sender} has {have} {op.resource}, needs {op.amount}"
        )

    new_world = world_state.copy()

    sender = new_world.countries[op.sender].copy()
    receiver = new_world.countries[op.receiver].copy()

    sender_res = dict(sender.resources)
    receiver_res = dict(receiver.resources)

    # subtract from sender
    sender_res[op.resource] = sender_res.get(op.resource, 0) - op.amount
    if sender_res[op.resource] < 0:
        # should not happen because can_transfer checked, but safe guard
        raise IllegalOperation(f"Resource '{op.resource}' went negative for sender")

    # add to receiver
    receiver_res[op.resource] = receiver_res.get(op.resource, 0) + op.amount

    sender.resources = sender_res
    receiver.resources = receiver_res

    new_world.countries[op.sender] = sender
    new_world.countries[op.receiver] = receiver

    return new_world
