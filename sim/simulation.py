from tda.avl import AVLTree
from tda.hash_map import HashMap
from domain.order import Order
from collections import deque
import streamlit as st

class Simulation:
    def __init__(self, graph):
        self.graph = graph
        self.orders = HashMap()
        self.clients = HashMap()
        self.route_log = AVLTree()
        self.order_id = 0
        self.origin_freq = {}
        self.dest_freq = {}
        
    def add_client(self, client):
        self.clients.insert(client.id, client)

    def create_order(self, origin, destination, client_id):
        path, cost = self.calculate_route(origin, destination)
        if path:
            st.write(f"ORDEN CREADA: {origin} → {destination} | Ruta: {' → '.join(path)} | Costo: {cost}")
            order = Order(self.order_id, origin, destination, path, cost, client_id)
            self.orders.insert(self.order_id, order)
            self.order_id += 1
            # Registrar ruta en AVL
            route_key = " → ".join(path)
            self.route_log.insert(route_key)
            # Registrar frecuencia de origen y destino
            self.origin_freq[origin] = self.origin_freq.get(origin, 0) + 1
            self.dest_freq[destination] = self.dest_freq.get(destination, 0) + 1
            return order
        st.write("NO SE CREÓ ORDEN (no hay ruta)")
        return None

    def calculate_route(self, origin, destination, battery_limit=50):

        # Guardar todas las rutas válidas encontradas
        all_routes = []

        queue = deque([(origin, [origin], 0)])
        while queue:
            current, path, cost = queue.popleft()
            if current == destination and cost <= battery_limit:
                all_routes.append((path, cost))
                continue

            for neighbor, weight in self.graph.get_neighbors(current):
                if neighbor not in path:  # Evita ciclos
                    new_cost = cost + weight

                    # Si supera batería y no es estación de recarga, no seguir
                    if new_cost > battery_limit:
                        if self.graph.vertices[neighbor].role != "recharge":
                            continue
                        new_cost = 0  # recarga

                    queue.append((neighbor, path + [neighbor], new_cost))

        if not all_routes:
            return None, None

        # Heurística: elegir la ruta más frecuente (según AVL), si empate, la de menor costo
        def route_frequency(route):
            key = " → ".join(route)
            node = self.route_log.root
            while node:
                if key == node.key:
                    return node.frequency
                elif key < node.key:
                    node = node.left
                else:
                    node = node.right
            return 0  # Si nunca se recorrió

        # Ordenar primero por frecuencia (desc), luego por costo (asc)
        all_routes.sort(key=lambda x: (-route_frequency(x[0]), x[1]))
        best_path, best_cost = all_routes[0]
        return best_path, best_cost

    def get_order(self, order_id):
        return self.orders.get(order_id)

    def get_orders(self):
        return self.orders.items()

    def get_clients(self):
        return self.clients.items()

    def get_route_frequencies(self):
        return self.route_log.inorder()
