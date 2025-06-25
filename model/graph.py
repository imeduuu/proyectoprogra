from model.vertex import Vertex

class Graph:
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, id, role="client"):
        if id not in self.vertices:
            self.vertices[id] = Vertex(id, role)

    def add_edge(self, from_id, to_id, weight):
        if from_id in self.vertices and to_id in self.vertices:
            self.vertices[from_id].add_neighbor(to_id, weight)
            self.vertices[to_id].add_neighbor(from_id, weight)

    def get_neighbors(self, id):
        if id in self.vertices:
            return self.vertices[id].get_neighbors()
        return []

    def has_edge(self, from_id, to_id):
        return (from_id in self.vertices and
                to_id in self.vertices[from_id].neighbors)

    def edge_count(self):
        counted = set()
        count = 0
        for vertex in self.vertices.values():
            for neighbor in vertex.neighbors:
                pair = tuple(sorted([vertex.id, neighbor]))
                if pair not in counted:
                    counted.add(pair)
                    count += 1
        return count
