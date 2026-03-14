from fastapi import APIRouter, HTTPException
from models.schemas import TransactionResponse, Transaction, Currency
from services.categorizer import get_category_summary

router = APIRouter()


@router.post("/transactions/summary")
async def get_summary(transactions: list[Transaction]):
    """
    Given a list of already-parsed transactions,
    return summary stats and category breakdown.
    """
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions provided.")

    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")
    category_summary = get_category_summary(transactions)
    currency = transactions[0].currency if transactions else Currency.INR

    return {
        "total_transactions": len(transactions),
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2),
        "net": round(total_credits - total_debits, 2),
        "currency": currency,
        "category_breakdown": category_summary,
    }


@router.post("/transactions/by-category")
async def get_by_category(transactions: list[Transaction], category: str):
    """Filter transactions by category."""
    filtered = [t for t in transactions if t.category and t.category.value.lower() == category.lower()]
    return {"category": category, "count": len(filtered), "transactions": filtered}
