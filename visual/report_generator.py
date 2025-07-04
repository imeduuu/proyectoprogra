from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os

class ReportGenerator:
    def __init__(self, sim):
        self.sim = sim

    def sanitize_text(self, text):
        reemplazos = {
            '→': '->',
            '✓': 'v',
            '—': '-',
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'",
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for original, reemplazo in reemplazos.items():
            text = text.replace(original, reemplazo)
        return text

    def generate_pdf(self):
        total_orders = len(list(self.sim.get_orders()))
        total_clients = len(list(self.sim.get_clients()))
        total_nodes = len(self.sim.graph.vertices)
        total_edges = self.sim.graph.edge_count()

        orders = list(self.sim.get_orders())
        clients = list(self.sim.get_clients())

        client_order_count = {}
        for _, order in orders:
            client_order_count[order.client_id] = client_order_count.get(order.client_id, 0) + 1
        top_clients = sorted(client_order_count.items(), key=lambda x: x[1], reverse=True)

        route_freq = self.sim.get_route_frequencies() if hasattr(self.sim, 'get_route_frequencies') else []
        top_routes = sorted(route_freq, key=lambda x: x[1], reverse=True)[:5]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte General del Sistema", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Total de ordenes: {total_orders}", ln=True)
        pdf.cell(200, 10, txt=f"Total de clientes: {total_clients}", ln=True)
        pdf.cell(200, 10, txt=f"Total de nodos: {total_nodes}", ln=True)
        pdf.cell(200, 10, txt=f"Total de aristas: {total_edges}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Tabla de Pedidos", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 8, "ID", 1)
        pdf.cell(40, 8, "Origen", 1)
        pdf.cell(40, 8, "Destino", 1)
        pdf.cell(40, 8, "Cliente", 1)
        pdf.cell(30, 8, "Estado", 1, ln=True)
        for _, order in orders:
            pdf.cell(40, 8, str(order.id), 1)
            pdf.cell(40, 8, self.sanitize_text(str(order.origin)), 1)
            pdf.cell(40, 8, self.sanitize_text(str(order.destination)), 1)
            pdf.cell(40, 8, self.sanitize_text(str(order.client_id)), 1)
            pdf.cell(30, 8, self.sanitize_text(str(order.status)), 1, ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Clientes con mas pedidos", ln=True)
        pdf.set_font("Arial", size=10)
        for client_id, count in top_clients[:5]:
            pdf.cell(0, 8, txt=self.sanitize_text(f"Cliente {client_id}: {count} pedidos"), ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Rutas mas usadas", ln=True)
        pdf.set_font("Arial", size=10)
        for route, freq in top_routes:
            pdf.cell(0, 8, txt=self.sanitize_text(f"Ruta {route}: {freq} veces"), ln=True)
        pdf.ln(5)

        if top_clients:
            fig, ax = plt.subplots(figsize=(4, 2))
            labels = [str(cid) for cid, _ in top_clients[:10]]
            values = [count for _, count in top_clients[:10]]
            ax.bar(labels, values, color='#1f77b4')
            ax.set_title('Pedidos por Cliente (Top 10)')
            ax.set_xlabel('Cliente')
            ax.set_ylabel('Pedidos')
            plt.tight_layout()
            tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(tmpfile.name)
            tmpfile.close()
            plt.close(fig)
            pdf.image(tmpfile.name, x=10, w=pdf.w - 20)
            os.unlink(tmpfile.name)
            pdf.ln(5)

        roles = [v.role for v in self.sim.graph.vertices.values()]
        total = len(roles)
        storage = roles.count('storage')
        recharge = roles.count('recharge')
        client = roles.count('client')
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Distribucion de roles de nodos", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, txt=f"Almacenamiento: {storage} ({storage / total:.0%})", ln=True)
        pdf.cell(0, 8, txt=f"Recarga: {recharge} ({recharge / total:.0%})", ln=True)
        pdf.cell(0, 8, txt=f"Cliente: {client} ({client / total:.0%})", ln=True)
        pdf.ln(5)

        roles_dict = {k: v.role for k, v in self.sim.graph.vertices.items()}
        origin_freq = getattr(self.sim, 'origin_freq', {})
        dest_freq = getattr(self.sim, 'dest_freq', {})
        total_freq = {node: origin_freq.get(node, 0) + dest_freq.get(node, 0) for node in self.sim.graph.vertices}
        storage_list = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'storage']
        recharge_list = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'recharge']
        client_list = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'client']
        top_storage = sorted(storage_list, key=lambda x: x[1], reverse=True)[:5]
        top_recharge = sorted(recharge_list, key=lambda x: x[1], reverse=True)[:5]
        top_client = sorted(client_list, key=lambda x: x[1], reverse=True)[:5]
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Nodos mas visitados por tipo (Top 5)", ln=True)
        pdf.set_font("Arial", size=10)
        for label, top in [("Storage", top_storage), ("Recharge", top_recharge), ("Client", top_client)]:
            pdf.cell(0, 8, txt=f"{label}:", ln=True)
            for node, freq in top:
                pdf.cell(0, 8, txt=self.sanitize_text(f"  Nodo {node}: {freq} visitas"), ln=True)
        pdf.ln(5)

        bar_labels = (
            [f"Storage {n}" for n, _ in top_storage] +
            [f"Recharge {n}" for n, _ in top_recharge] +
            [f"Client {n}" for n, _ in top_client]
        )
        bar_values = (
            [f for _, f in top_storage] +
            [f for _, f in top_recharge] +
            [f for _, f in top_client]
        )
        if bar_labels:
            fig2, ax2 = plt.subplots(figsize=(5, 2))
            ax2.bar(bar_labels, bar_values, color=['#1f77b4'] * len(top_storage) + ['#2ca02c'] * len(top_recharge) + ['#ff7f0e'] * len(top_client))
            ax2.set_ylabel("Frecuencia de visitas (origen + destino)")
            ax2.set_xticks(range(len(bar_labels)))
            ax2.set_xticklabels(bar_labels, rotation=45, ha='right')
            plt.tight_layout()
            tmpfile2 = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(tmpfile2.name)
            tmpfile2.close()
            plt.close(fig2)
            pdf.image(tmpfile2.name, x=10, w=pdf.w - 20)
            os.unlink(tmpfile2.name)
            pdf.ln(5)

        return pdf.output(dest='S').encode('latin1', errors='replace')
