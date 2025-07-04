from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class OrderIn(BaseModel):
    origin: str
    destination: str
    client_id: str

from sim.global_simulation import get_simulation

@router.get("/")
def get_orders():
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return [order.to_dict() for _, order in sim.get_orders()]

@router.get("/{order_id}")
def get_order(order_id: int):
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    order = sim.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order.to_dict()

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int):
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    order = sim.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.status not in ["In Progress"]:
        raise HTTPException(status_code=400, detail="La orden no puede ser cancelada")
    order.status = "Cancelled"
    return {"message": f"Orden {order_id} cancelada exitosamente."}

@router.post("/{order_id}/complete")
def complete_order(order_id: int):
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    order = sim.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.status not in ["In Progress"]:
        raise HTTPException(status_code=400, detail="La orden no puede ser completada")
    order.complete_order()
    return {"message": f"Orden {order_id} marcada como completada."}

@router.post("/")
def create_order(order: OrderIn):
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    # Validar que el cliente existe
    clientes = sim.get_clients()
    cliente = None
    for c in clientes:
        # c puede ser tupla (id, obj) o solo objeto
        obj = c[1] if isinstance(c, tuple) else c
        if str(obj.id) == str(order.client_id):
            cliente = obj
            break
    if not cliente:
        raise HTTPException(status_code=400, detail="El cliente especificado no existe.")
    # Validar que el nodo origen existe y es de tipo 'storage'
    if order.origin not in sim.graph.vertices:
        raise HTTPException(status_code=400, detail="El nodo de origen no existe en el grafo.")
    if sim.graph.vertices[order.origin].role != "storage":
        raise HTTPException(status_code=400, detail="El nodo de origen debe ser de tipo 'storage'.")
    # Validar que el nodo destino existe y es de tipo 'client'
    if order.destination not in sim.graph.vertices:
        raise HTTPException(status_code=400, detail="El nodo de destino no existe en el grafo.")
    if sim.graph.vertices[order.destination].role != "client":
        raise HTTPException(status_code=400, detail="El nodo de destino debe ser de tipo 'client'.")
    # Validar que el cliente está asignado al nodo destino
    if str(cliente.node_id) != str(order.destination):
        raise HTTPException(status_code=400, detail="El cliente no está asignado al nodo de destino.")
    sim.create_order(order.origin, order.destination, order.client_id)
    return {"message": "Orden creada correctamente"}