from fpdf import FPDF

class ReportGenerator:
    def __init__(self, sim):
        self.sim = sim

    def generate_pdf(self):
        total_orders = len(list(self.sim.get_orders()))
        total_clients = len(list(self.sim.get_clients()))
        total_nodes = len(self.sim.graph.vertices)
        total_edges = self.sim.graph.edge_count()

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
        for _, order in self.sim.get_orders():
            pdf.cell(200, 10, txt=f"Orden {order.id}: {order.origin} -> {order.destination} | Estado: {order.status}", ln=True)
        return pdf.output(dest='S').encode('latin1')