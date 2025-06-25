from fastapi import FastAPI
from sim.init_simulation import SimulationInitializer
from sim.simulation import Simulation
from api.controllers import client_routes, order_routes, report_routes, info_routes

app = FastAPI()

# Instancia global de simulación (puedes mejorar esto según tus necesidades)
sim = None

def get_simulation():
    global sim
    return sim

@app.on_event("startup")
def startup_event():
    global sim
    # Inicializa la simulación aquí o crea un endpoint para inicializarla
    initializer = SimulationInitializer(15, 20)
    graph = initializer.generate_connected_graph()
    sim = Simulation(graph)

app.include_router(client_routes.router)
app.include_router(order_routes.router)
app.include_router(report_routes.router)
app.include_router(info_routes.router)