class Route:
    def __init__(self, path, cost):
        self.path = path
        self.cost = cost

    def to_string(self):
        return f"{' → '.join(self.path)} | Cost: {self.cost}"

    def __str__(self):
        return self.to_string()
