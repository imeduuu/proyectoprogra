from model.vertex import Vertex
import heapq

class Graph:
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, id, role="client", lat=None, lon=None):
        if id not in self.vertices:
            self.vertices[id] = Vertex(id, role, lat, lon)

    def add_edge(self, from_id, to_id, weight):
        if from_id in self.vertices and to_id in self.vertices:
            self.vertices[from_id].add_neighbor(to_id, weight)
            self.vertices[to_id].add_neighbor(from_id, weight)  # Grafo no dirigido

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
                edge = tuple(sorted((vertex.id, neighbor)))
                if edge not in counted:
                    counted.add(edge)
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

    def floyd_warshall(self):
        # Devuelve distancias y caminos entre todos los pares
        nodes = list(self.vertices.keys())
        n = len(nodes)
        dist = {u: {v: float('inf') for v in nodes} for u in nodes}
        next_node = {u: {v: None for v in nodes} for u in nodes}

        for u in nodes:
            dist[u][u] = 0
            next_node[u][u] = u
            for v, w in self.get_neighbors(u):
                dist[u][v] = w
                next_node[u][v] = v

        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]

        # Función para reconstruir el camino
        def get_path(u, v):
            if next_node[u][v] is None:
                return []
            path = [u]
            while u != v:
                u = next_node[u][v]
                path.append(u)
            return path

        return dist, get_path

    def kruskal_mst(self):
        # Kruskal para MST: retorna lista de aristas [(from, to, weight), ...]
        parent = {}
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        def union(u, v):
            pu, pv = find(u), find(v)
            if pu != pv:
                parent[pu] = pv

        edges = []
        for u in self.vertices:
            for v, w in self.get_neighbors(u):
                if u < v:  # evitar duplicados
                    edges.append((w, u, v))
        edges.sort()
        for v in self.vertices:
            parent[v] = v

        mst = []
        for w, u, v in edges:
            if find(u) != find(v):
                union(u, v)
                mst.append((u, v, w))
        return mst
