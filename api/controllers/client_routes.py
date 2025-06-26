from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ClientIn(BaseModel):
    id: str
    name: str
    node_id: str
    priority: int

@router.get("/clients/")
def get_clients():
    from api.main import get_simulation  # Import aquí
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return [client.to_dict() for _, client in sim.get_clients()]

@router.get("/clients/{client_id}")
def get_client(client_id: str):
    from api.main import get_simulation  # Import aquí
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    for cid, client in sim.get_clients():
        if str(cid) == str(client_id):
            return client.to_dict()
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

# ----------- AGREGA ESTE BLOQUE -----------
@router.post("/clients/")
def add_client(client: ClientIn):
    from api.main import get_simulation
    from domain.client import Client as DomainClient
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    # Crea y agrega el cliente a la simulación
    new_client = DomainClient(client.id, client.name, client.node_id, client.priority)
    sim.add_client(new_client)
    return {"message": "Cliente agregado correctamente"}
# ------------------------------------------