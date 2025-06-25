from fastapi import APIRouter, HTTPException

router = APIRouter()

def get_visit_ranking(sim, role_type):
    # Suma visitas de origen y destino
    freq = {}
    for node, count in sim.origin_freq.items():
        freq[node] = freq.get(node, 0) + count
    for node, count in sim.dest_freq.items():
        freq[node] = freq.get(node, 0) + count
    # Filtra por tipo de nodo
    result = [
        {"node_id": node, "visits": freq[node]}
        for node in sim.graph.vertices
        if sim.graph.vertices[node].role == role_type
    ]
    # Ordena descendente
    return sorted(result, key=lambda x: x["visits"], reverse=True)

@router.get("/reports/visits/clients")
def visits_clients():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return get_visit_ranking(sim, "client")

@router.get("/reports/visits/recharges")
def visits_recharges():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return get_visit_ranking(sim, "recharge")

@router.get("/reports/visits/storages")
def visits_storages():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return get_visit_ranking(sim, "storage")

@router.get("/reports/summary")
def simulation_summary():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    total_orders = len(list(sim.get_orders()))
    total_clients = len(list(sim.get_clients()))
    total_nodes = len(sim.graph.vertices)
    total_edges = sim.graph.edge_count()
    return {
        "total_orders": total_orders,
        "total_clients": total_clients,
        "total_nodes": total_nodes,
        "total_edges": total_edges
    }