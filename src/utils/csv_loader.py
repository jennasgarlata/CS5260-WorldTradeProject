import pandas as pd
from models.country import Country
from models.world_state import WorldState


def load_resource_weights(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    # Ensure weights are floats
    return {str(r): float(w) for r, w in zip(df["resource"], df["weight"])}


def load_world_state(filepath: str) -> WorldState:
    df = pd.read_csv(filepath)
    countries = []

    for _, row in df.iterrows():
        name = str(row["Country"])

        raw = row.drop("Country").to_dict()
        resources = {}
        for k, v in raw.items():
            if pd.isna(v):
                resources[str(k)] = 0
            else:
                # be tolerant: allow "10" or 10.0
                resources[str(k)] = int(float(v))

        countries.append(Country(name=name, resources=resources))

    return WorldState(countries)