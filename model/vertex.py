class Vertex:
    def __init__(self, id, role="client"):
        self.id = id
        self.role = role
        self.neighbors = {} 

    def add_neighbor(self, neighbor_id, weight):
        self.neighbors[neighbor_id] = weight

    def get_neighbors(self):
        return self.neighbors.items()
