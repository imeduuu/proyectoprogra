from fastapi import APIRouter, HTTPException, Response
from fpdf import FPDF

router = APIRouter()

@router.get("/reports/pdf")
def get_pdf_report():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    total_orders = len(list(sim.get_orders()))
    total_clients = len(list(sim.get_clients()))
    total_nodes = len(sim.graph.vertices)
    total_edges = sim.graph.edge_count()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte General del Sistema", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total de órdenes: {total_orders}", ln=True)
    pdf.cell(200, 10, txt=f"Total de clientes: {total_clients}", ln=True)
    pdf.cell(200, 10, txt=f"Total de nodos: {total_nodes}", ln=True)
    pdf.cell(200, 10, txt=f"Total de aristas: {total_edges}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Órdenes:", ln=True)
    for _, order in sim.get_orders():
        pdf.cell(200, 10, txt=f"Orden {order.id}: {order.origin} -> {order.destination} | Estado: {order.status}", ln=True)
    pdf_output = pdf.output(dest='S').encode('latin1')
    return Response(content=pdf_output, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})