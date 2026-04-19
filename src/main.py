from scheduler.country_scheduler import country_scheduler
import time

def run_depth_experiment(depth):
    result = country_scheduler(
        your_country_name="Narnia",
        resources_filename="data/resource_weights.csv",
        initial_state_filename="data/initial_world.csv",
        output_schedule_filename=f"data/output_schedules_depth_{depth}.txt",
        num_output_schedules=20,
        depth_bound=depth, 
        frontier_max_size=100,
        templates_dir="data/templates/transforms",
        multiplier_cap=5,
        transfer_amount_cap=5,
        successor_keep_probability=0.5,
        random_seed=42,
    )

def run_beam_experiment(beam):
    result = country_scheduler(
        your_country_name="Narnia",
        resources_filename="data/resource_weights.csv",
        initial_state_filename="data/initial_world.csv",
        output_schedule_filename=f"data/output_schedules_beam_{beam}.txt",
        num_output_schedules=20,
        depth_bound=8, 
        frontier_max_size=beam,
        templates_dir="data/templates/transforms",
        multiplier_cap=5,
        transfer_amount_cap=5,
        successor_keep_probability=0.5,
        random_seed=42,
    )

def run_pruning_experiment(keep_p):
    result = country_scheduler(
        your_country_name="Narnia",
        resources_filename="data/resource_weights.csv",
        initial_state_filename="data/initial_world.csv",
        output_schedule_filename=f"data/output_schedules_pruning_{keep_p}.txt",
        num_output_schedules=20,
        depth_bound=8, 
        frontier_max_size=100,
        templates_dir="data/templates/transforms",
        multiplier_cap=5,
        transfer_amount_cap=5,
        successor_keep_probability=keep_p,
        random_seed=42,
    )

def run_standard(itr):
    start = time.time()
    result = country_scheduler(
        your_country_name="Narnia",
        resources_filename="data/resource_weights.csv",
        initial_state_filename="data/initial_world.csv",
        output_schedule_filename=f"data/output_schedules_{itr}.txt",
        num_output_schedules=10,
        depth_bound=8, 
        frontier_max_size=100,
        templates_dir="data/templates/transforms",
        multiplier_cap=5,
        transfer_amount_cap=5,
        successor_keep_probability=.5,
        random_seed=None,
    )
    end = time.time()
    print(f"Elapsed time: {end - start:.4f} seconds")

def run_experiments():
    print("\nRunning depth experiments...")
    for e in [2,4,6,8,10,12]:
        print(f"\nRunning experiment for depth={e}\n")
        start = time.time()
        run_depth_experiment(e)
        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds")

    print("\nDepth experiments finished")

    print("\nRunning beam experiments...")
    for e in [5, 10, 25, 50, 100, 250]:
        print(f"\nRunning experiment for beam={e}\n")
        start = time.time()
        run_beam_experiment(e)
        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds")

    print("\nBeam experiments finished")

    print("\nRunning pruning experiments...")
    for e in [0.05,0.1,0.25,0.5,0.75,1]:
        print(f"\nRunning experiment for successor_keep_probability={e}\n")
        start = time.time()
        run_pruning_experiment(e)
        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds")

    print("\nPruning experiments finished")

def main():
    for i in [1,2,3,4,5]:
      run_standard(i)



if __name__ == "__main__":
    main()