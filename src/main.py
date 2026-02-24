# from utils.csv_loader import load_world_state
# from models.transfer import TransferOperation
# from models.transform import TransformOperation, TransformTemplate
# from ops.transfer_engine import apply_transfer
# from ops.transform_engine import apply_transform


# def print_world(world):
#     print("\n--- WORLD STATE ---")
#     for name, country in world.countries.items():
#         print(name, country.resources)


# def main():

#     # -------------------------
#     # Load world from CSV
#     # -------------------------
#     world = load_world_state("data/initial_world.csv")

#     print("Initial state:")
#     print_world(world)

#     # -------------------------
#     # TEST TRANSFER
#     # -------------------------
#     transfer_op = TransferOperation(
#         sender="Narnia",      # use real country names from your CSV
#         receiver="Genovia",
#         resource="Timber",
#         amount=1
#     )

#     world = apply_transfer(world, transfer_op)

#     print("\nAfter TRANSFER:")
#     print_world(world)

#     # -------------------------
#     # TEST TRANSFORM
#     # -------------------------

#     # Minimal test template
#     templates = {
#         "Housing": TransformTemplate(
#             name="Housing",
#             inputs={
#                 "Population": 1,
#             },
#             outputs={
#                 "Housing": 1,
#                 "Population": 1
#             }
#         )
#     }

#     transform_op = TransformOperation(
#         country="Narnia",
#         template_name="Housing",
#         multiplier=1
#     )

#     world = apply_transform(world, transform_op, templates)

#     print("\nAfter TRANSFORM:")
#     print_world(world)


# if __name__ == "__main__":
#     main()
from utils.csv_loader import load_world_state
from utils.transform_parser import load_transform_templates_dir

from models.transfer import TransferOperation
from models.transform import TransformOperation

from ops.transfer_engine import apply_transfer
from ops.transform_engine import apply_transform


def print_world(world):
    print("\n--- WORLD STATE ---")
    for name, country in world.countries.items():
        print(name, country.resources)


def main():
    # -------------------------
    # Load world from CSV
    # -------------------------
    world = load_world_state("data/initial_world.csv")

    print("Initial state:")
    print_world(world)

    # -------------------------
    # Load transform templates (real files)
    # -------------------------
    templates = load_transform_templates_dir("data/templates/transforms")
    print("\nLoaded transform templates:", sorted(templates.keys()))

    # -------------------------
    # TEST TRANSFER
    # -------------------------
    transfer_op = TransferOperation(
        sender="Narnia",
        receiver="Genovia",
        resource="Timber",
        amount=1
    )

    world = apply_transfer(world, transfer_op)

    print("\nAfter TRANSFER:")
    print_world(world)

    # -------------------------
    # TEST TRANSFORM (uses real template)
    # -------------------------
    transform_op = TransformOperation(
        country="Narnia",
        template_name="Alloys",
        multiplier=1
    )

    world = apply_transform(world, transform_op, templates)

    print("\nAfter TRANSFORM (Alloys x1):")
    print_world(world)


if __name__ == "__main__":
    main()