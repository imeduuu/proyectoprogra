import streamlit as st
import requests
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"  # Cambia si tu API corre en otro puerto

def run():
    st.title("🚁 Sistema Logístico Autónomo con Drones (API Backend)")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔄 Run Simulation",
        "🌍 Explore Network",
        "🌐 Clients & Orders",
        "📋 Route Analytics",
        "📈 General Statistics"
    ])

    # --- Pestaña 1: Run Simulation ---
    with tab1:
        st.header("🔄 Run Simulation")
        n_nodes = st.slider("Cantidad de nodos", 10, 150, 30)
        m_edges = st.slider("Cantidad de aristas", n_nodes-1, 300, max(n_nodes, n_nodes+10))
        n_orders = st.slider("Cantidad de órdenes", 10, 300, 30)
        st.info("20% almacenamiento, 20% recarga, 60% clientes")
        if st.button("📊 Start Simulation"):
            resp = requests.post(f"{API_URL}/simulation/start", json={
                "n_nodes": n_nodes,
                "m_edges": m_edges,
                "n_orders": n_orders
            })
            if resp.status_code == 200:
                st.success("Simulación iniciada correctamente.")
            else:
                st.error("Error al iniciar simulación.")

    # --- Pestaña 2: Explore Network ---
    with tab2:
        st.header("🌍 Explore Network")
        # Obtener nodos y aristas desde la API
        nodes_resp = requests.get(f"{API_URL}/graph/nodes")
        edges_resp = requests.get(f"{API_URL}/graph/edges")
        if nodes_resp.status_code == 200 and edges_resp.status_code == 200:
            nodes = nodes_resp.json()
            edges = edges_resp.json()
            # Mostrar nodos y aristas (puedes usar folium aquí si tienes coordenadas)
            st.write("Nodos:", nodes)
            st.write("Aristas:", edges)
        else:
            st.warning("No se pudo obtener la red desde la API.")

        # Selectbox para rutas
        storages = [n["id"] for n in nodes if n["role"] == "storage"] if nodes_resp.status_code == 200 else []
        clients = [n["id"] for n in nodes if n["role"] == "client"] if nodes_resp.status_code == 200 else []
        origin = st.selectbox("Origen (Almacenamiento)", storages)
        destination = st.selectbox("Destino (Cliente)", clients)
        algorithm = st.radio("Algoritmo de ruta", ["Dijkstra"], horizontal=True)
        if st.button("✈️ Calculate Route"):
            route_resp = requests.get(f"{API_URL}/routes/calculate", params={
                "origin": origin,
                "destination": destination,
                "algorithm": algorithm.lower()
            })
            if route_resp.status_code == 200:
                route_data = route_resp.json()
                st.success(f"Ruta: {route_data['path']} | Costo: {route_data['cost']}")
            else:
                st.error("No se pudo calcular la ruta.")

        if st.button("🌲 Show MST (Kruskal)"):
            mst_resp = requests.get(f"{API_URL}/graph/mst")
            if mst_resp.status_code == 200:
                st.write("MST:", mst_resp.json())
            else:
                st.error("No se pudo obtener el MST.")

    # --- Pestaña 3: Clients & Orders ---
    with tab3:
        st.header("🌐 Clients & Orders (API)")
        # Listar clientes
        clients_response = requests.get(f"{API_URL}/clients/")
        if clients_response.status_code == 200:
            clients = clients_response.json()
            st.subheader("Clientes")
            st.json(clients)
        else:
            st.error("No se pudieron obtener los clientes desde la API.")

        # Listar órdenes
        orders_response = requests.get(f"{API_URL}/orders/")
        if orders_response.status_code == 200:
            orders = orders_response.json()
            st.subheader("Órdenes")
            st.json(orders)
        else:
            st.error("No se pudieron obtener las órdenes desde la API.")

        # Crear cliente
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

    # --- Pestaña 4: Route Analytics ---
    with tab4:
        st.header("📋 Route Analytics")
        freq_resp = requests.get(f"{API_URL}/routes/frequencies")
        if freq_resp.status_code == 200:
            frequencies = freq_resp.json()
            st.write("Rutas más frecuentes:")
            for route in frequencies:
                st.write(f"{route['path']} → {route['frequency']} veces")
        else:
            st.info("No hay rutas registradas aún.")

        if st.button("📄 Generar Informe PDF"):
            pdf_resp = requests.get(f"{API_URL}/reports/pdf")
            if pdf_resp.status_code == 200:
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_resp.content,
                    file_name="informe_rutas.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("No se pudo generar el PDF.")

    # --- Pestaña 5: General Statistics ---
    with tab5:
        st.header("📈 General Statistics")
        stats_resp = requests.get(f"{API_URL}/stats/general")
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            st.json(stats)
            # Ejemplo de gráfico de torta
            labels = ['Almacenamiento', 'Recarga', 'Cliente']
            sizes = [stats['storage_count'], stats['recharge_count'], stats['client_count']]
            colors = ['#1f77b4', '#2ca02c', '#ff7f0e']
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle.
            st.pyplot(fig)
        else:
            st.error("No se pudieron obtener las estadísticas generales.")

if __name__ == "__main__":
    run()