from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.utils.reporting import create_monthly_report_pdf

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/monthly/pdf")
def monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        buffer = create_monthly_report_pdf(current_user, db, month, year)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=monthly_report_{month}_{year}.pdf"},
    )
