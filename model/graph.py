from model.vertex import Vertex
import heapq

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

    def dijkstra(self, origin, destination):
        # Inicialización
        queue = []
        heapq.heappush(queue, (0, origin, [origin]))
        visited = set()

        while queue:
            cost, current, path = heapq.heappop(queue)
            if current == destination:
                return path, cost
            if current in visited:
                continue
            visited.add(current)
            for neighbor, weight in self.get_neighbors(current):
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
        return None, float('inf')

    def kruskal_mst(self):
        parent = {}
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        def union(u, v):
            pu, pv = find(u), find(v)
            parent[pu] = pv

        # Inicializar conjuntos
        for v in self.vertices:
            parent[v] = v

        # Obtener todas las aristas (u, v, peso)
        edges = []
        for u in self.vertices:
            for v, w in self.get_neighbors(u):
                if u < v:  # Evitar duplicados en grafo no dirigido
                    edges.append((w, u, v))
        edges.sort()  # Ordenar por peso

        mst = []
        for w, u, v in edges:
            if find(u) != find(v):
                mst.append((u, v, w))
                union(u, v)
        return mst
