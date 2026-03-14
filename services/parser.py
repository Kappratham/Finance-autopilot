import fitz  # PyMuPDF
import uuid
from services.llm import chat_json
from models.schemas import Transaction, ParsedStatement, Currency


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def detect_currency(text: str) -> Currency:
    """Quick heuristic currency detection before LLM call."""
    text_lower = text.lower()
    inr_signals = ["₹", "inr", "rupee", "rs.", "rs "]
    usd_signals = ["$", "usd", "dollar"]

    inr_count = sum(text_lower.count(s) for s in inr_signals)
    usd_count = sum(text_lower.count(s) for s in usd_signals)

    return Currency.INR if inr_count >= usd_count else Currency.USD


def parse_statement(file_bytes: bytes) -> ParsedStatement:
    """
    Main parser pipeline:
    1. Extract raw text via PyMuPDF
    2. LLM detects bank format and extracts transactions
    3. Return structured ParsedStatement
    """
    raw_text = extract_text_from_pdf(file_bytes)

    if not raw_text.strip():
        raise ValueError("Could not extract text from PDF. File may be scanned/image-based.")

    currency = detect_currency(raw_text)
    currency_symbol = "₹" if currency == Currency.INR else "$"

    # Limit text sent to LLM to avoid token overflow
    # Send first 3000 chars for format detection + full text for transactions
    preview_text = raw_text[:3000]
    full_text = raw_text[:12000]  # cap at ~12K chars for token safety

    SYSTEM_PROMPT = f"""You are a financial document parser specializing in Indian and US bank statements.
Your job is to extract all transactions from a bank statement and return them as structured JSON.

Rules:
- Detect the bank name from the document header
- Identify the account holder name if present
- Identify the statement period if present  
- Currency is {currency.value} ({currency_symbol})
- Extract ALL transactions with: date, description, amount, type (debit/credit), balance
- Normalize dates to YYYY-MM-DD format
- Amount should always be a positive float — use type field for debit/credit
- If balance is not present, set it to null
- Return ONLY valid JSON, no explanation

Return this exact structure:
{{
  "bank_name": "string",
  "account_holder": "string or null",
  "statement_period": "string or null",
  "transactions": [
    {{
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 0.00,
      "type": "debit or credit",
      "balance": 0.00 or null
    }}
  ]
}}"""

    USER_PROMPT = f"""Parse this bank statement and extract all transactions:

{full_text}"""

    result = chat_json(SYSTEM_PROMPT, USER_PROMPT)

    # Build Transaction objects
    transactions = []
    for i, t in enumerate(result.get("transactions", [])):
        try:
            transactions.append(Transaction(
                id=str(uuid.uuid4()),
                date=t.get("date", ""),
                description=t.get("description", ""),
                amount=float(t.get("amount", 0)),
                type=t.get("type", "debit").lower(),
                currency=currency,
                balance=t.get("balance"),
                category=None  # filled by categorizer
            ))
        except Exception:
            continue  # skip malformed transactions

    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")

    return ParsedStatement(
        bank_name=result.get("bank_name", "Unknown Bank"),
        account_holder=result.get("account_holder"),
        statement_period=result.get("statement_period"),
        currency=currency,
        total_credits=round(total_credits, 2),
        total_debits=round(total_debits, 2),
        transactions=transactions
    )
