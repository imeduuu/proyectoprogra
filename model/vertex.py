class Vertex:
    def __init__(self, id, role="client", lat=None, lon=None):
        self.id = id
        self.role = role
        self.neighbors = {}
        self.lat = lat  # Nueva propiedad para latitud
        self.lon = lon  # Nueva propiedad para longitud

    def add_neighbor(self, neighbor_id, weight):
        self.neighbors[neighbor_id] = weight

    def get_neighbors(self):
        return self.neighbors.items()
