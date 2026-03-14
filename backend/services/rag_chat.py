import math
from services.llm import chat
from models.schemas import Transaction, Currency

# In-memory store — no external dependencies needed
_indexed_transactions = []
_indexed_texts = []


def _simple_tokenize(text: str) -> set:
    """Simple word tokenizer for similarity matching."""
    return set(text.lower().replace(",", " ").replace(".", " ").split())


def _cosine_similarity(text1: str, text2: str) -> float:
    """Simple TF-based cosine similarity without external libraries."""
    tokens1 = _simple_tokenize(text1)
    tokens2 = _simple_tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    return len(intersection) / math.sqrt(len(tokens1) * len(tokens2))


def _transaction_to_text(t: Transaction, symbol: str) -> str:
    """Convert a transaction to a searchable text chunk."""
    return (
        f"On {t.date}, {t.description} — "
        f"{symbol}{t.amount:,.2f} ({t.type.upper()}) "
        f"Category: {t.category.value if t.category else 'Uncategorized'}. "
        f"{'Balance after: ' + symbol + str(t.balance) if t.balance else ''}"
    ).strip()


def index_transactions(transactions: list[Transaction]) -> int:
    """
    Index transactions into memory for RAG chat.
    Called once after upload + categorization.
    """
    global _indexed_transactions, _indexed_texts

    if not transactions:
        return 0

    currency = transactions[0].currency
    symbol = "₹" if currency == Currency.INR else "$"

    _indexed_transactions = transactions
    _indexed_texts = [_transaction_to_text(t, symbol) for t in transactions]

    return len(transactions)


def _retrieve_relevant(query: str, top_k: int = 10) -> list[str]:
    """Retrieve most relevant transaction texts for a query."""
    if not _indexed_texts:
        return []

    scored = [
        (i, _cosine_similarity(query, text))
        for i, text in enumerate(_indexed_texts)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_k]

    return [_indexed_texts[i] for i, _ in top if _ > 0]


def chat_with_finances(
    question: str,
    transactions: list[Transaction],
    chat_history: list[dict] = None
) -> dict:
    """
    RAG chat over transactions.
    Retrieves relevant transactions, then LLM answers grounded in data.
    """
    if not transactions:
        return {
            "answer": "No transactions loaded. Please upload a bank statement first.",
            "sources": []
        }

    currency = transactions[0].currency
    symbol = "₹" if currency == Currency.INR else "$"

    total_debits = sum(t.amount for t in transactions if t.type == "debit")
    total_credits = sum(t.amount for t in transactions if t.type == "credit")

    # If not indexed yet, index on the fly
    if not _indexed_texts or len(_indexed_texts) != len(transactions):
        index_transactions(transactions)

    retrieved_docs = _retrieve_relevant(question, top_k=10)

    # Fallback to all transactions if nothing retrieved
    if not retrieved_docs:
        retrieved_docs = _indexed_texts[:15]

    context = "\n".join(retrieved_docs)

    # Build conversation history
    history_text = ""
    if chat_history:
        for msg in chat_history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    SYSTEM_PROMPT = f"""You are a personal finance assistant helping a user understand their bank transactions.
You have access to their actual transaction data. Answer questions based ONLY on the provided data.
Be specific — use actual amounts, dates, and merchant names from the data.
If you cannot find the answer in the provided transactions, say so honestly.
Currency: {currency.value} ({symbol})
Total spending this period: {symbol}{total_debits:,.2f}
Total income this period: {symbol}{total_credits:,.2f}"""

    USER_PROMPT = f"""Relevant transactions for this question:
{context}

{f'Previous conversation:{chr(10)}{history_text}' if history_text else ''}

User question: {question}

Answer based on the transaction data above. Be specific with amounts and dates."""

    answer = chat(SYSTEM_PROMPT, USER_PROMPT)

    return {
        "answer": answer,
        "sources": retrieved_docs[:3],
        "retrieved_count": len(retrieved_docs),
    }
