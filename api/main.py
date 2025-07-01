from fastapi import FastAPI
from api.controllers import client_routes, order_routes, report_routes, info_routes

app = FastAPI()

from sim.global_simulation import get_simulation

app.include_router(client_routes.router, prefix="/clients")
app.include_router(order_routes.router, prefix="/orders")
app.include_router(report_routes.router, prefix="/reports")
app.include_router(info_routes.router, prefix="/info")