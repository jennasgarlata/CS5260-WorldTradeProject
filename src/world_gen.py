import pandas as pd
import random

def generate_random_world(input_file, output_file, seed=None):
    """
    Reads a CSV of country resources and generates a new one with:
    - 0 values preserved
    - All other values randomized between 10 and 50
    """

    if seed is not None:
        random.seed(seed)

    # Load CSV
    df = pd.read_csv(input_file)

    # Assume first column is country name (non-numeric)
    for col in df.columns[1:]:  # skip country column
        df[col] = df[col].apply(lambda x: 0 if x == 0 else random.randint(10, 50))

    # Save new CSV
    df.to_csv(output_file, index=False)

    print(f"Generated file saved to: {output_file}")


if __name__ == "__main__":
    input_file = "data/initial_world.csv"
    output_file = "data/randomized_world.csv"

    generate_random_world(input_file, output_file, seed=42)