import streamlit as st
from sim.init_simulation import SimulationInitializer
from sim.simulation import Simulation
from visual.networkx_adapter import NetworkXAdapter
from visual.avl_visualizer import AVLVisualizer
from domain.client import Client
import matplotlib.pyplot as plt
import requests
from visual.map.map_builder import MapBuilder
from streamlit_folium import st_folium

# --- NUEVO: Importa el global_simulation y threading/uvicorn ---
from sim.global_simulation import set_simulation
import threading
import uvicorn

API_URL = "http://127.0.0.1:8000"

# --- NUEVO: Lanza FastAPI como thread si no está corriendo ---
def run_api():
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False, log_level="warning")

if 'api_thread' not in st.session_state:
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    st.session_state.api_thread = api_thread

if 'sim' not in st.session_state:
    st.session_state.sim = None     
if 'graph_adapter' not in st.session_state:
    st.session_state.graph_adapter = None
if 'order_success' not in st.session_state:
    st.session_state.order_success = False 

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
        min_edges = n_nodes - 1
        default_edges = max(min_edges, 20)
        m_edges = st.slider("Número de aristas", min_edges, 300, default_edges) 
        n_orders = st.slider("Número de órdenes", 10, 300, 10) 

        if st.button("📊 Start Simulation"):   
            initializer = SimulationInitializer(n_nodes, m_edges)
            graph = initializer.generate_connected_graph()
            sim = Simulation(graph)
            st.session_state.sim = sim
            st.session_state.graph_adapter = NetworkXAdapter(graph)
            set_simulation(sim) 
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
            st.markdown("""
**Leyenda de colores:**
<span style='color:#1f77b4'>●</span> Almacenamiento &nbsp;&nbsp;
<span style='color:#2ca02c'>●</span> Recarga &nbsp;&nbsp;
<span style='color:#ff7f0e'>●</span> Cliente
""", unsafe_allow_html=True)

    with tab2:
        st.header("🌍 Explore Network")
        if st.session_state.sim:
            graph = st.session_state.sim.graph

            # Selección de nodos
            storage_nodes = [v.id for v in graph.vertices.values() if v.role == "storage"]
            client_nodes = [v.id for v in graph.vertices.values() if v.role == "client"]
            origin = st.selectbox("Origen (Almacenamiento)", storage_nodes)
            destination = st.selectbox("Destino (Cliente)", client_nodes)

            # Algoritmo
            algorithm = st.radio("Algoritmo a utilizar", ["Dijkstra", "Floyd-Warshall"])

            # Calcular ruta
            if st.button("✈ Calculate Route"):
                if algorithm == "Dijkstra":
                    path, cost = graph.dijkstra(origin, destination)
                else:
                    dist, get_path = graph.floyd_warshall()
                    path = get_path(origin, destination)
                    cost = dist[origin][destination] if path else float('inf')
                if path and cost != float('inf'):
                    st.session_state.calculated_path = path
                    st.session_state.calculated_cost = cost
                else:
                    st.session_state.calculated_path = None
                    st.session_state.calculated_cost = None

            # Mostrar/ocultar MST (Kruskal) como toggle
            if "show_mst" not in st.session_state:
                st.session_state.show_mst = False

            if st.button("🌲 Mostrar/ocultar MST (Kruskal)"):
                st.session_state.show_mst = not st.session_state.show_mst

            # Construir el mapa
            map_builder = MapBuilder()
            # Colores por rol
            color_map = {"storage": "blue", "recharge": "green", "client": "orange"}

            # Agregar nodos
            for v in graph.vertices.values():
                lat = getattr(v, "lat", None)
                lon = getattr(v, "lon", None)
                if lat is not None and lon is not None:
                    map_builder.add_node(lat, lon, popup=f"{v.id} ({v.role})", color=color_map.get(v.role, "gray"))

            # Agregar aristas normales
            for v in graph.vertices.values():
                for neighbor_id, _ in v.get_neighbors():
                    if v.id < neighbor_id:  # Evita duplicados
                        neighbor = graph.vertices[neighbor_id]
                        map_builder.add_edge((v.lat, v.lon), (neighbor.lat, neighbor.lon), color="gray")

            # Resaltar ruta calculada
            if st.session_state.get("calculated_path"):
                path = st.session_state.calculated_path
                for i in range(len(path) - 1):
                    v1 = graph.vertices[path[i]]
                    v2 = graph.vertices[path[i+1]]
                    map_builder.add_edge((v1.lat, v1.lon), (v2.lat, v2.lon), color="red")

            # Resaltar MST si corresponde (usando toggle)
            if st.session_state.show_mst:
                mst_edges = graph.kruskal_mst()
                for u, v, _ in mst_edges:
                    v1 = graph.vertices[u]
                    v2 = graph.vertices[v]
                    map_builder.add_edge((v1.lat, v1.lon), (v2.lat, v2.lon), color="blue")
                st.info(f"Árbol de Expansión Mínima: {len(mst_edges)} aristas, peso total: {sum(w for _, _, w in mst_edges)}")

            # Mostrar el mapa en Streamlit
            st_folium(map_builder.get_map(), width=700, height=500)

            # Mostrar resumen de ruta
            if st.session_state.get("calculated_path"):
                st.success(f"Ruta: {' → '.join(st.session_state.calculated_path)} | Costo: {st.session_state.calculated_cost}")

            # Mostrar resumen MST
            if st.session_state.get("mst_edges"):
                st.info(f"Árbol de Expansión Mínima: {len(st.session_state.mst_edges)} aristas, peso total: {sum(w for _, _, w in st.session_state.mst_edges)}")

        # Botón para completar orden
        if st.button("✅ Completar Orden"):
            clientes = st.session_state.sim.get_clients()
            # Validar que exista un cliente en el nodo destino
            cliente_en_destino = any(str(c[1].node_id) == str(destination) for c in clientes)
            if not cliente_en_destino:
                st.error("Debe existir un cliente creado en el nodo de destino para completar la orden.")
            elif not st.session_state.get("calculated_path"):
                st.error("Debe calcular una ruta antes de completar la orden.")
            else:
                # Busca el id del cliente en el nodo destino
                cliente_id = None
                for c in clientes:
                    if str(c[1].node_id) == str(destination):
                        cliente_id = c[1].id
                        break
                if cliente_id is not None:
                    st.session_state.sim.create_order(origin, destination, client_id=cliente_id)
                    st.success("Orden completada y registrada correctamente.")
                else:
                    st.error("No se pudo encontrar el cliente en el nodo destino.")

    with tab3:
        st.header("🌐 Clients & Orders (API)")
        if st.button("🔄 Recargar datos de la API"):
            st.session_state['reload_api'] = True

        # Luego, usa reload_api para volver a consultar la API
        if st.session_state.get('reload_api', False):
            clients_response = requests.get(f"{API_URL}/clients/")
            orders_response = requests.get(f"{API_URL}/orders/")
            st.session_state['reload_api'] = False
        else:
            clients_response = requests.get(f"{API_URL}/clients/")
            orders_response = requests.get(f"{API_URL}/orders/")

        # Mostrar clientes desde la API
        if clients_response.status_code == 200:
            clients = clients_response.json()
            st.subheader("Clientes")
            st.json(clients)
        else:
            st.error("No se pudieron obtener los clientes desde la API.")

        # Mostrar órdenes desde la API
        if orders_response.status_code == 200:
            orders = orders_response.json()
            st.subheader("Órdenes")
            st.json(orders)
        else:
            st.error("No se pudieron obtener las órdenes desde la API.")

        # Formulario para agregar cliente usando la API
        with st.form("add_client_form"):
            client_id = st.text_input("ID del cliente")
            client_name = st.text_input("Nombre del cliente")
            node_id = st.text_input("Nodo donde se ubicará el cliente")
            priority = st.selectbox("Prioridad", [1, 2, 3, 4, 5], index=0)
            submit = st.form_submit_button("Agregar cliente")
            if submit:
                client_data = {
                    "id": client_id,
                    "name": client_name,
                    "node_id": node_id,
                    "priority": priority
                }
                resp = requests.post(f"{API_URL}/clients/", json=client_data)
                if resp.status_code == 200:
                    st.success("Cliente agregado correctamente.")
                else:
                    st.error("Error al agregar cliente.")

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

            total_freq = {}
            for node in st.session_state.sim.graph.vertices.keys():
                total_freq[node] = (
                    st.session_state.sim.origin_freq.get(node, 0) +
                    st.session_state.sim.dest_freq.get(node, 0)
                )

            storage = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'storage']
            recharge = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'recharge']
            client = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'client']

            top_storage = sorted(storage, key=lambda x: x[1], reverse=True)[:5]
            top_recharge = sorted(recharge, key=lambda x: x[1], reverse=True)[:5]
            top_client = sorted(client, key=lambda x: x[1], reverse=True)[:5]

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
                ax2.bar(bar_labels, bar_values,
                        color=['#1f77b4']*len(top_storage) +
                              ['#2ca02c']*len(top_recharge) +
                              ['#ff7f0e']*len(top_client))
                ax2.set_ylabel("Frecuencia de visitas (origen + destino)")
                ax2.set_xticks(range(len(bar_labels)))
                ax2.set_xticklabels(bar_labels, rotation=45, ha='right')
                st.pyplot(fig2)
            else:
                st.info("Aún no hay visitas registradas en los nodos.")

            # 🔽 BOTÓN PARA DESCARGAR EL PDF
            st.subheader("📄 Descargar Reporte PDF")
            if st.button("📥 Generar informe PDF"):
                try:
                    response = requests.get("http://127.0.0.1:8000/reports/reports/pdf")  
                    if response.status_code == 200:
                        st.success("✅ Informe generado correctamente.")
                        st.download_button(
                            label="⬇️ Haz clic aquí para descargar el PDF",
                            data=response.content,
                            file_name="reporte.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error(f"❌ Error al generar el PDF: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ No se pudo conectar al servidor: {e}")

if __name__ == "__main__":
    run()
