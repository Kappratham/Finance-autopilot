from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.report import generate_monthly_report
from models.schemas import Transaction

router = APIRouter()


class ReportRequest(BaseModel):
    transactions: list[Transaction]
    month: str = None
    compare_transactions: list[Transaction] = None  # previous month for comparison


@router.post("/report/generate")
async def generate_report(request: ReportRequest):
    """
    Generate a plain English monthly financial report.
    Optionally include compare_transactions for month-over-month analysis.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided.")

    try:
        report = generate_monthly_report(
            transactions=request.transactions,
            month=request.month,
            compare_transactions=request.compare_transactions,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
