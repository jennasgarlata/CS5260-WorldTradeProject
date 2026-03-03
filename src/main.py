from utils.csv_loader import load_world_state, load_resource_weights
from utils.transform_parser import load_transform_templates_dir

from SearchStrategies.GreedyBestFirstSearch import GreedyBestFirstSearch

from models.schedule_state import ScheduleState
from models.transform_action import TransformAction
from eval.eu_heuristic import EUHeuristic
from eval.state_quality import set_resource_weights

from models.transform import TransformOperation
from models.transfer import TransferOperation
from models.transfer_action import TransferAction


def build_transfer_actions(world, self_country: str, max_depth: int, amount_cap: int = 1):
    actions = []

    countries = list(world.countries.keys())
    base_amounts = sorted({1, amount_cap})  # avoids duplicate [1,1]

    # Explicitly forbidden structural / demographic resources
    FORBIDDEN_RESOURCES = {"Population", "Housing", "AvailableLand"}

    for sender in countries:
        for receiver in countries:
            if sender == receiver:
                continue

            # Only allow transfers involving self_country
            if self_country not in (sender, receiver):
                continue

            sender_country = world.get_country(sender)

            # Only resources that exist, are positive, and are allowed
            resources = []
            for r, amt in sender_country.resources.items():
                if int(amt) <= 0:
                    continue
                if r in FORBIDDEN_RESOURCES:
                    continue
                if r.endswith("Waste"):   # block ALL waste transfers
                    continue
                resources.append(r)

            for res in resources:
                have = int(sender_country.get(res))
                for amt in base_amounts:
                    if 1 <= amt <= have:
                        op = TransferOperation(
                            sender=sender,
                            receiver=receiver,
                            resource=res,
                            amount=amt,
                        )
                        actions.append(TransferAction(op, max_depth))

    return actions

def build_actions(world, templates, self_country: str, max_depth: int, multiplier_cap: int = 10):
    """
    Build transform actions for the self_country only.
    """
    actions = []

    for template_name in templates.keys():
        for k in range(1, multiplier_cap + 1):
            op = TransformOperation(
                country=self_country,
                template_name=template_name,
                multiplier=k,
            )
            actions.append(TransformAction(op, templates, max_depth))

    return actions


class DepthGoal:
    """
    Goal sentinel that matches ANY state with depth >= max_depth.
    This avoids issues if multiple ScheduleState classes exist or imports differ.
    """
    def __init__(self, max_depth: int):
        self.max_depth = max_depth

    def __eq__(self, other) -> bool:
        return hasattr(other, "depth") and other.depth >= self.max_depth


def extract_goal_node(solution):
    """
    Works across common professor Solution implementations.
    Returns a Node or None.
    """
    if solution is None:
        return None

    # Most common attribute names
    for attr in ["GOAL_NODE", "goal_node", "goalNode", "NODE", "node"]:
        if hasattr(solution, attr):
            return getattr(solution, attr)

    # Sometimes stored as first field or similar; last resort: inspect __dict__
    d = getattr(solution, "__dict__", {})
    for k, v in d.items():
        # Heuristic: Node usually has STATE attribute
        if hasattr(v, "STATE"):
            return v

    return None


def main():
    # ----------------------------
    # Load inputs
    # ----------------------------
    world = load_world_state("data/initial_world.csv")
    weights = load_resource_weights("data/resource_weights.csv")
    templates = load_transform_templates_dir("data/templates/transforms")

    set_resource_weights(weights)

    print("\nInitial state:\n")
    print("--- WORLD STATE ---")
    print(world)
    print("\nLoaded transform templates:", list(templates.keys()))

    # ----------------------------
    # Agent/search settings
    # ----------------------------
    self_country = "Narnia"
    max_depth = 7

    from eval.state_quality import Q
    for country_name in world.countries.keys():
        print(f"Q({country_name}) initial: {Q(country_name, world)}")

    # IMPORTANT: use tree-based search (ScheduleState contains WorldState which is not hashable)
    search = GreedyBestFirstSearch(tree_based_search=True)

    start = ScheduleState(world=world, schedule=tuple(), depth=0)

    transform_actions = build_actions(
        world=world,
        templates=templates,
        self_country=self_country,
        max_depth=max_depth,
        multiplier_cap=10,
    )

    transfer_actions = build_transfer_actions(world=world, self_country=self_country, max_depth=max_depth, amount_cap=1)

    actions = transform_actions + transfer_actions
    heuristic = EUHeuristic(self_country=self_country, initial_world=world, templates=templates)

    # Goal is any state with depth >= max_depth
    goals = [DepthGoal(max_depth)]

    # ----------------------------
    # Run search
    # ----------------------------
    solution = search.search(
        initial_state=start,
        actions=actions,
        heuristic=heuristic,
        goals=goals,
    )

    # ----------------------------
    # Print results
    # ----------------------------
    if solution is None:
        print("\nSearch returned None.")
        return

    # Professor Solution stores PATH as a list of Node objects
    path = getattr(solution, "PATH", None)
    if not path:
        print("\nNo PATH found on Solution.")
        print("Solution dict:", getattr(solution, "__dict__", {}))
        return

    goal_node = path[-1]  # last node in the solution path
    final_state = goal_node.STATE

    print("\n--- BEST SCHEDULE FOUND (GBFS) ---")
    for op in final_state.schedule:
        print(" ", op)

    print("\n--- FINAL WORLD ---")
    print(final_state.world)
    for country_name in world.countries.keys():
        print(f"Q({country_name}) final: {Q(country_name, final_state.world)}")

    visited = getattr(solution, "VISITED", [])
    print("\nVisited states:", len(visited))


if __name__ == "__main__":
    main()