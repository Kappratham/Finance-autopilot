from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_chat import chat_with_finances, index_transactions
from models.schemas import Transaction

router = APIRouter()


class IndexRequest(BaseModel):
    transactions: list[Transaction]


class ChatRequest(BaseModel):
    question: str
    transactions: list[Transaction]
    chat_history: list[dict] = []  # [{"role": "user/assistant", "content": "..."}]


@router.post("/chat/index")
async def index(request: IndexRequest):
    """
    Index transactions into ChromaDB for RAG chat.
    Call this once after upload before starting chat.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided.")

    try:
        count = index_transactions(request.transactions)
        return {
            "success": True,
            "indexed": count,
            "message": f"Successfully indexed {count} transactions. You can now chat with your data."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/chat/message")
async def message(request: ChatRequest):
    """
    Ask a question about your financial data.
    Supports multi-turn conversation via chat_history.

    Example questions:
    - How much did I spend on food this month?
    - What was my biggest expense?
    - Did I spend more on Swiggy or Zomato?
    - How much did I save this month?
    - Show me all transactions above ₹2000
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided.")

    try:
        result = chat_with_finances(
            question=request.question,
            transactions=request.transactions,
            chat_history=request.chat_history,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
