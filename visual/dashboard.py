import streamlit as st
from sim.init_simulation import SimulationInitializer
from sim.simulation import Simulation
from visual.networkx_adapter import NetworkXAdapter
from visual.avl_visualizer import AVLVisualizer
from domain.client import Client
import matplotlib.pyplot as plt

if 'sim' not in st.session_state: # Inicializar la simulación
    st.session_state.sim = None     
if 'graph_adapter' not in st.session_state: # Inicializar el adaptador de NetworkX
    st.session_state.graph_adapter = None
if 'order_success' not in st.session_state: # Inicializar el flag de éxito de orden
    st.session_state.order_success = False 
#prueba
def run(): 
    st.title("🚁 Sistema Logístico Autónomo con Drones")        

    tab1, tab2, tab3, tab4, tab5 = st.tabs([    
        "🔄 Run Simulation",
        "🌍 Explore Network",
        "🌐 Clients & Orders",
        "📋 Route Analytics",
        "📈 General Statistics"
    ])
#configurar las pestañas
    with tab1: 
        st.header("🔄 Run Simulation") 
        n_nodes = st.slider("Número de nodos", 10, 150, 15) 
        m_edges = st.slider("Número de aristas", n_nodes - 1, 300, 20) 
        n_orders = st.slider("Número de órdenes", 10, 300, 10) 

        if st.button("📊 Start Simulation"):   
            initializer = SimulationInitializer(n_nodes, m_edges)
            graph = initializer.generate_connected_graph()
            st.session_state.sim = Simulation(graph)
            st.session_state.graph_adapter = NetworkXAdapter(graph)
            st.success("Simulación iniciada")

        # Mostrar resumen y grafo si la simulación ya está creada
        if st.session_state.sim:
            roles = [v.role for v in st.session_state.sim.graph.vertices.values()]
            total = len(roles)
            storage = roles.count('storage')
            recharge = roles.count('recharge')
            client = roles.count('client')
            st.info(
                f"**Nodos:** {total}  \n"
                f"Almacenamiento: {storage} ({storage/total:.0%})  \n"
                f"Recarga: {recharge} ({recharge/total:.0%})  \n"
                f"Cliente: {client} ({client/total:.0%})"
            )
            st.markdown(f"**Nodos:** {len(st.session_state.sim.graph.vertices)}  \n**Aristas:** {st.session_state.sim.graph.edge_count()}")
            fig = st.session_state.graph_adapter.draw_graph()
            st.pyplot(fig)

    with tab2:
        st.header("🌍 Explore Network")
        if st.session_state.sim:
            available_nodes = list(st.session_state.sim.graph.vertices.keys())
            origin = st.selectbox("Origen", available_nodes, key="origin_input")
            destination = st.selectbox("Destino", available_nodes, key="destination_input")

            # Calcular ruta y guardarla en session_state
            if st.button("✈ Calculate Route"):
                path, cost = st.session_state.sim.calculate_route(origin, destination)
                if path:
                    st.session_state.calculated_path = path
                    st.session_state.calculated_cost = cost
                    st.session_state.calculated_origin = origin
                    st.session_state.calculated_destination = destination
                else:
                    st.session_state.calculated_path = None
                    st.session_state.calculated_cost = None
                    st.session_state.calculated_origin = None
                    st.session_state.calculated_destination = None

            # Mostrar grafo resaltando la ruta si existe
            highlight_edges = None
            if st.session_state.get("calculated_path"):
                p = st.session_state.calculated_path
                highlight_edges = list(zip(p, p[1:]))
            fig = st.session_state.graph_adapter.draw_graph(highlight_edges=highlight_edges)
            st.pyplot(fig)

            st.markdown("""
            **Leyenda de colores:**
            <span style='color:#1f77b4'>●</span> Almacenamiento &nbsp;&nbsp;
            <span style='color:#2ca02c'>●</span> Recarga &nbsp;&nbsp;
            <span style='color:#ff7f0e'>●</span> Cliente
            """, unsafe_allow_html=True)

            # Mostrar ruta si existe en session_state
            if st.session_state.get("calculated_path"):
                st.write(f"**Ruta:** {' → '.join(st.session_state.calculated_path)} | **Costo:** {st.session_state.calculated_cost}")

                # Selecciona el cliente asociado a la orden
                clients = list(st.session_state.sim.get_clients())
                if clients:
                    client_ids = [client[0] for client in clients]
                    selected_client_id = st.selectbox("Cliente asociado a la orden", client_ids, key="order_client_selectbox")
                    if st.button("✅ Complete Delivery and Create Order"):
                        st.session_state.sim.create_order(
                            st.session_state.calculated_origin,
                            st.session_state.calculated_destination,
                            selected_client_id
                        )
                        st.session_state.order_success = True
                else:
                    st.info("Debe agregar al menos un cliente antes de crear una orden.")
            elif "calculated_path" in st.session_state and st.session_state.calculated_path is None:
                st.error("No hay ruta disponible con autonomía")

    with tab3:
        st.header("🌐 Clients & Orders")
        if st.session_state.sim:
            # Mostrar mensaje de éxito si existe el flag
            if st.session_state.order_success:
                st.success("Orden generada y ruta registrada")
                st.session_state.order_success = False

            with st.form("add_client_form"):
                client_id = st.text_input("ID del cliente", value=str(len(st.session_state.sim.clients.keys()) + 1))
                client_name = st.text_input("Nombre del cliente", value=f"Cliente {client_id}")
                # Selecciona nodo del grafo
                available_nodes = list(st.session_state.sim.graph.vertices.keys())
                node_id = st.selectbox("Nodo donde se ubicará el cliente", available_nodes)
                # Selecciona prioridad
                priority = st.selectbox("Prioridad", [1, 2, 3, 4, 5], index=0)
                submit = st.form_submit_button("Agregar cliente")

                if submit:
                    client = Client(client_id, client_name, node_id, priority)
                    st.session_state.sim.add_client(client)
                    st.success(f"Cliente {client.name} agregado en nodo {node_id} con prioridad {priority}")

            st.subheader("Clientes")
            clients_list = []
            for client_id, client in st.session_state.sim.get_clients():
                role = st.session_state.sim.graph.vertices[client.node_id].role if client.node_id in st.session_state.sim.graph.vertices else None
                clients_list.append(client.to_dict(role=role))
            st.json(clients_list)

            # Mostrar órdenes con nombre de cliente asociado
            orders_list = []
            clients_dict = {client[0]: client[1] for client in st.session_state.sim.get_clients()}
            for order_id, order in st.session_state.sim.get_orders():
                client_name = clients_dict[order.client_id].name if order.client_id in clients_dict else None
                orders_list.append(order.to_dict(client_name=client_name))
            st.subheader("Órdenes")
            st.json(orders_list)

    with tab4:
        st.header("📋 Route Analytics")
        if st.session_state.sim:
            frequencies = st.session_state.sim.get_route_frequencies()
            st.write("Rutas más frecuentes:")

            # Ordenar rutas por frecuencia descendente
            if frequencies:
                sorted_freq = sorted(frequencies, key=lambda x: x[1], reverse=True)
                for route, freq in sorted_freq:
                    st.write(f"{route} → {freq} veces")

                # Mostrar la ruta más frecuente
                ruta_mas_frecuente = sorted_freq[0]
                st.info(f"Ruta más frecuente: {ruta_mas_frecuente[0]} ({ruta_mas_frecuente[1]} veces)")
            else:
                st.write("No hay rutas registradas aún.")

            if st.button("📊 Visualizar AVL Tree"):
                visualizer = AVLVisualizer(st.session_state.sim.route_log)
                fig = visualizer.draw()
                st.pyplot(fig)

    with tab5:
        st.header("📈 General Statistics")
        if st.session_state.sim:
            roles = [v.role for v in st.session_state.sim.graph.vertices.values()]
            total = len(roles)
            storage = roles.count('storage')
            recharge = roles.count('recharge')
            client = roles.count('client')
            st.info(
                f"**Nodos:** {total}  \n"
                f"Almacenamiento: {storage} ({storage/total:.0%})  \n"
                f"Recarga: {recharge} ({recharge/total:.0%})  \n"
                f"Cliente: {client} ({client/total:.0%})"
            )
            fig = st.session_state.graph_adapter.draw_graph()
            st.pyplot(fig)

            # Mostrar frecuencia de nodos origen y destino
            st.subheader("Frecuencia de nodos origen")
            st.json(st.session_state.sim.origin_freq)
            st.subheader("Frecuencia de nodos destino")
            st.json(st.session_state.sim.dest_freq)

            # Calcular los nodos más visitados por tipo usando las frecuencias
            roles_dict = {k: v.role for k, v in st.session_state.sim.graph.vertices.items()}

            # Combina frecuencias de origen y destino para cada nodo
            total_freq = {}
            for node in st.session_state.sim.graph.vertices.keys():
                total_freq[node] = st.session_state.sim.origin_freq.get(node, 0) + st.session_state.sim.dest_freq.get(node, 0)

            # Agrupa por tipo de nodo
            storage = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'storage']
            recharge = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'recharge']
            client = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'client']

            # Toma los 5 más visitados de cada tipo
            top_storage = sorted(storage, key=lambda x: x[1], reverse=True)[:5]
            top_recharge = sorted(recharge, key=lambda x: x[1], reverse=True)[:5]
            top_client = sorted(client, key=lambda x: x[1], reverse=True)[:5]

            # Prepara datos para el gráfico de barras
            bar_labels = (
                [f"Storage {n}" for n, _ in top_storage] +
                [f"Recharge {n}" for n, _ in top_recharge] +
                [f"Client {n}" for n, _ in top_client]
            )
            bar_values = (
                [f for _, f in top_storage] +
                [f for _, f in top_recharge] +
                [f for _, f in top_client]
            )

            if bar_labels:
                st.subheader("Nodos más visitados por tipo")
                fig2, ax2 = plt.subplots()
                ax2.bar(bar_labels, bar_values, color=['#1f77b4']*len(top_storage) + ['#2ca02c']*len(top_recharge) + ['#ff7f0e']*len(top_client))
                ax2.set_ylabel("Frecuencia de visitas (origen + destino)")
                ax2.set_xticks(range(len(bar_labels))) 
                ax2.set_xticklabels(bar_labels, rotation=45, ha='right')
                st.pyplot(fig2)
            else:
                st.info("Aún no hay visitas registradas en los nodos.")

if __name__ == "__main__":
    run()