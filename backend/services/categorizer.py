from services.llm import chat_json
from models.schemas import Transaction, Category


CATEGORIES = [c.value for c in Category]

SYSTEM_PROMPT = """You are a financial transaction categorizer.
Given a list of bank transactions, assign each one a category.

Available categories:
- Food (restaurants, grocery, food delivery, cafes, swiggy, zomato, uber eats)
- Transport (fuel, uber, ola, metro, train, flight, parking, fastag)
- Utilities (electricity, water, internet, phone bill, gas, broadband)
- Entertainment (movies, netflix, spotify, gaming, events, amazon prime)
- Shopping (clothing, amazon, flipkart, retail, electronics, online shopping)
- Healthcare (pharmacy, hospital, doctor, medical, health insurance)
- Transfers (bank transfer, neft, imps, upi transfer, wallet, self transfer)
- Income (salary, cashback, refund, interest, dividend, credit received)
- Other (anything that does not fit above)

Rules:
- Use description keywords to determine category
- UPI payments: try to infer from merchant name
- ATM withdrawals → Other
- EMI/loan payments → Transfers
- Return ONLY valid JSON

Input will be a list of transactions with id and description.
Return this exact structure:
{
  "categorized": [
    {"id": "transaction-id", "category": "CategoryName"}
  ]
}"""


def categorize_transactions(transactions: list[Transaction]) -> list[Transaction]:
    """
    Batch categorize transactions using Groq LLM.
    Processes in batches of 50 to stay within token limits.
    """
    if not transactions:
        return transactions

    # Build input list
    batch_size = 50
    categorized_map = {}

    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]

        batch_input = [
            {"id": t.id, "description": t.description, "amount": t.amount, "type": t.type}
            for t in batch
        ]

        user_prompt = f"Categorize these transactions:\n{batch_input}"

        try:
            result = chat_json(SYSTEM_PROMPT, user_prompt)
            for item in result.get("categorized", []):
                categorized_map[item["id"]] = item["category"]
        except Exception:
            # If batch fails, mark all as Other
            for t in batch:
                categorized_map[t.id] = "Other"

    # Apply categories back to transactions
    for transaction in transactions:
        raw_category = categorized_map.get(transaction.id, "Other")
        try:
            transaction.category = Category(raw_category)
        except ValueError:
            transaction.category = Category.OTHER

    return transactions


def get_category_summary(transactions: list[Transaction]) -> dict:
    """
    Returns spending breakdown by category.
    Only counts debits (actual spending).
    """
    summary = {}
    for t in transactions:
        if t.type == "debit" and t.category:
            cat = t.category.value
            summary[cat] = round(summary.get(cat, 0) + t.amount, 2)

    # Sort by amount descending
    return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))
