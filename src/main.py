from scheduler.country_scheduler import country_scheduler

def run_depth_experiment(depth):
    result = country_scheduler(
        your_country_name="Narnia",
        resources_filename="data/resource_weights.csv",
        initial_state_filename="data/initial_world.csv",
        output_schedule_filename=f"data/output_schedules_depth_{depth}.txt",
        num_output_schedules=20,
        depth_bound=depth,  # only thing changing
        frontier_max_size=10000,
        templates_dir="data/templates/transforms",
        multiplier_cap=5,
        transfer_amount_cap=5,
        successor_keep_probability=0.1,
        random_seed=42,
    )


def main():
    # result = country_scheduler(
    #     your_country_name="Narnia",
    #     resources_filename="data/resource_weights.csv",
    #     initial_state_filename="data/initial_world.csv",
    #     output_schedule_filename="data/output_schedules.txt",
    #     num_output_schedules=5,
    #     depth_bound=7,
    #     frontier_max_size=10000,
    #     templates_dir="data/templates/transforms",
    #     multiplier_cap=5,
    #     transfer_amount_cap=5,
    #     successor_keep_probability=0.1,
    #     random_seed=42,
    # )

    print("\nRunning depth experiments...")
    for e in [2,4,6,8]:
        print(f"\nRunning experiment for depth={e}")
        run_depth_experiment(e)

    print("\nDepth experiment finished")

if __name__ == "__main__":
    main()