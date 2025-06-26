from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class OrderIn(BaseModel):
    origin: str
    destination: str
    client_id: str

@router.get("/orders/")
def get_orders():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    return [order.to_dict() for _, order in sim.get_orders()]

@router.get("/orders/{order_id}")
def get_order(order_id: int):
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    order = sim.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order.to_dict()

@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    from api.main import get_simulation
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

@router.post("/orders/{order_id}/complete")
def complete_order(order_id: int):
    from api.main import get_simulation
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

@router.post("/orders/")
def create_order(order: OrderIn):
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    # Crea la orden en la simulación del backend
    sim.create_order(order.origin, order.destination, order.client_id)
    return {"message": "Orden creada correctamente"}