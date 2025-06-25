from fastapi import APIRouter, HTTPException, Response
from visual.report_generator import ReportGenerator

router = APIRouter()

@router.get("/reports/pdf")
def get_pdf_report():
    from api.main import get_simulation
    sim = get_simulation()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no inicializada")
    pdf_bytes = ReportGenerator(sim).generate_pdf()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})