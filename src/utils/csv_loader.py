import pandas as pd
from models.country import Country
from models.world_state import WorldState


def load_resource_weights(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    return dict(zip(df["resource"], df["weight"]))


def load_world_state(filepath: str) -> WorldState:
    df = pd.read_csv(filepath)
    countries = []

    for _, row in df.iterrows():
        name = row["Country"]
        resources = row.drop("Country").to_dict()
        countries.append(Country(name=name, resources=resources))

    return WorldState(countries)
