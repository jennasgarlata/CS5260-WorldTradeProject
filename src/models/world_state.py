class WorldState:
    def __init__(self, countries):
        self.countries = {c.name: c for c in countries}

    def get_country(self, name):
        return self.countries[name]

    def __repr__(self):
        return "\n".join(str(c) for c in self.countries.values())

    def copy(self):
        return WorldState([
            country.copy()
            for country in self.countries.values()
        ])

