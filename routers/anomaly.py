from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.anomaly import detect_anomalies
from models.schemas import Transaction

router = APIRouter()


class AnomalyRequest(BaseModel):
    transactions: list[Transaction]


@router.post("/anomaly/detect")
async def detect(request: AnomalyRequest):
    """
    Detect unusual spending patterns.
    Uses statistical analysis + LLM explanation.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided.")

    try:
        result = detect_anomalies(request.transactions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")
