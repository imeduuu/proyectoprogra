from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ClientIn(BaseModel):
    name: str
    node_id: str
    priority: int

from sim.global_simulation import get_simulation

@router.get("/")
def get_clients():
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    # Devuelve el rol real del nodo asociado a cada cliente
    result = []
    for _, client in sim.get_clients():
        node = sim.graph.vertices.get(client.node_id)
        role = node.role if node else None
        result.append(client.to_dict(role=role))
    return result

@router.get("/{client_id}")
def get_client(client_id: str):
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    for cid, client in sim.get_clients():
        if str(cid) == str(client_id):
            return client.to_dict()
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@router.post("/")
def add_client(client: ClientIn):
    from domain.client import Client as DomainClient
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    # Validar que el nodo existe
    if client.node_id not in sim.graph.vertices:
        raise HTTPException(status_code=400, detail="El nodo especificado no existe en el grafo.")
    # Validar que el nodo es de tipo 'client'
    if sim.graph.vertices[client.node_id].role != "client":
        raise HTTPException(status_code=400, detail="Solo se pueden asignar clientes a nodos de tipo 'client'.")
    # Generar ID automático creciente
    existing_ids = [int(c[0]) for c in sim.get_clients() if str(c[0]).isdigit()]
    next_id = str(max(existing_ids) + 1) if existing_ids else "0"
    new_client = DomainClient(next_id, client.name, client.node_id, client.priority)
    sim.add_client(new_client)
    return {"message": "Cliente agregado correctamente", "id": next_id}