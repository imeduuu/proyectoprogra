import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self, avl_tree):
        self.tree = avl_tree

    def draw(self):
        G = nx.DiGraph()
        self._add_edges(self.tree.root, G)
        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')

        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=1200, node_color="lightblue", ax=ax)
        return fig  # Devuelve la figura para usar con st.pyplot(fig)

    def _add_edges(self, node, G):
        if node:
            G.add_node(node.key, label=f"{node.key}\nFreq: {node.frequency}")
            if node.left:
                G.add_edge(node.key, node.left.key)
                self._add_edges(node.left, G)
            if node.right:
                G.add_edge(node.key, node.right.key)
                self._add_edges(node.right, G)
