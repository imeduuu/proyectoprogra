import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    def __init__(self, graph):
        self.graph = graph

    def to_networkx(self):
        G = nx.Graph()
        for vertex in self.graph.vertices.values():
            G.add_node(vertex.id, role=vertex.role)
        for vertex in self.graph.vertices.values():
            for neighbor, weight in vertex.neighbors.items():
                if not G.has_edge(vertex.id, neighbor):
                    G.add_edge(vertex.id, neighbor, weight=weight)
        return G

    def draw_graph(self, highlight_edges=None):
        G = self.to_networkx()
        pos = nx.spring_layout(G, seed=42)

        # Colores según rol
        colors = []
        for node in G.nodes(data=True):
            role = node[1]['role']
            if role == 'storage':
                colors.append('blue')
            elif role == 'recharge':
                colors.append('green')
            else:
                colors.append('orange')

        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=500, ax=ax)

        # Dibujar aristas resaltadas en rojo si se especifican
        if highlight_edges:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=highlight_edges,
                width=3,
                edge_color='red',
                ax=ax
            )

        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
        return fig
