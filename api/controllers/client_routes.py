from fastapi import APIRouter, HTTPException

router = APIRouter()

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