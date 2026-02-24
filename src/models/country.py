class Country:
    def __init__(self, name, resources):
        self.name = name
        self.resources = resources  # dict

    def get(self, resource):
        return self.resources.get(resource, 0)

    def update(self, resource, amount):
        self.resources[resource] = self.get(resource) + amount

    def __repr__(self):
        return f"{self.name}: {self.resources}"

    def copy(self):
        return Country(self.name, dict(self.resources))
