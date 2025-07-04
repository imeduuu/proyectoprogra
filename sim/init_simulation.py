import random
from model.graph import Graph

class SimulationInitializer:
    def __init__(self, n_nodes, m_edges):
        self.n_nodes = n_nodes
        self.m_edges = m_edges
        self.graph = Graph()

    def generate_connected_graph(self):
        # Crear nodos con latitud y longitud aleatoria en Temuco
        for i in range(self.n_nodes):
            lat = random.uniform(-38.76, -38.70)
            lon = random.uniform(-72.65, -72.55)
            self.graph.add_vertex(str(i), lat=lat, lon=lon)

        # Asignar roles
        self.assign_roles()

        # Crear al menos un árbol conexo (n-1 aristas)
        nodes = list(self.graph.vertices.keys())
        random.shuffle(nodes)
        for i in range(self.n_nodes - 1):
            weight = random.randint(1, 20)  # valor aleatorio de peso en las aristas
            self.graph.add_edge(nodes[i], nodes[i + 1], weight)

        # Añadir aristas extra al azar hasta completar m_edges
        while self.graph.edge_count() < self.m_edges:
            u, v = random.sample(nodes, 2)
            if not self.graph.has_edge(u, v):
                weight = random.randint(1, 20)
                self.graph.add_edge(u, v, weight)

        return self.graph

    def assign_roles(self):
        n_storage = int(self.n_nodes * 0.2)
        n_recharge = int(self.n_nodes * 0.2)
        n_clients = self.n_nodes - n_storage - n_recharge

        roles = (["storage"] * n_storage +
                 ["recharge"] * n_recharge +
                 ["client"] * n_clients)
        random.shuffle(roles)

        for i, role in enumerate(roles):
            self.graph.vertices[str(i)].role = role
