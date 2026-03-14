from services.llm import chat
from services.categorizer import get_category_summary
from models.schemas import Transaction, Currency


def generate_monthly_report(
    transactions: list[Transaction],
    month: str = None,
    compare_transactions: list[Transaction] = None
) -> dict:
    """
    Generate a plain English monthly financial report.
    Optionally accepts a previous month's transactions for comparison.
    """
    if not transactions:
        return {"error": "No transactions provided."}

    currency = transactions[0].currency
    symbol = "₹" if currency == Currency.INR else "$"

    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")
    net = total_credits - total_debits
    category_summary = get_category_summary(transactions)

    # Top 5 largest expenses
    top_expenses = sorted(
        [t for t in transactions if t.type == "debit"],
        key=lambda x: x.amount,
        reverse=True
    )[:5]

    top_expenses_text = "\n".join([
        f"- {t.date}: {t.description} — {symbol}{t.amount:,.2f} ({t.category.value if t.category else 'Uncategorized'})"
        for t in top_expenses
    ])

    category_text = "\n".join([
        f"- {cat}: {symbol}{amount:,.2f}"
        for cat, amount in category_summary.items()
    ])

    # Month over month comparison
    comparison_text = ""
    mom_data = {}
    if compare_transactions:
        prev_summary = get_category_summary(compare_transactions)
        prev_total = sum(t.amount for t in compare_transactions if t.type == "debit")
        curr_total = total_debits

        for cat, curr_amt in category_summary.items():
            prev_amt = prev_summary.get(cat, 0)
            if prev_amt > 0:
                change_pct = ((curr_amt - prev_amt) / prev_amt) * 100
                mom_data[cat] = {
                    "current": curr_amt,
                    "previous": prev_amt,
                    "change_pct": round(change_pct, 1)
                }

        overall_change = ((curr_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
        comparison_text = f"""
Month-over-Month:
- Previous month total spending: {symbol}{prev_total:,.2f}
- Current month total spending: {symbol}{curr_total:,.2f}
- Overall change: {overall_change:+.1f}%
Category changes: {mom_data}
"""

    SYSTEM_PROMPT = """You are a personal finance advisor giving honest, plain English monthly reports.
Your tone is direct, helpful, and slightly conversational — like a smart friend who knows finance.
Never be preachy. Be specific. Use the actual numbers.
Always end with exactly 3 actionable suggestions based on the data.
Format your response in clear sections."""

    USER_PROMPT = f"""Generate a monthly financial report for this data:

Period: {month or 'This Month'}
Currency: {currency.value} ({symbol})

Summary:
- Total Income/Credits: {symbol}{total_credits:,.2f}
- Total Spending/Debits: {symbol}{total_debits:,.2f}
- Net: {symbol}{net:,.2f} ({'saved' if net > 0 else 'overspent'})
- Total transactions: {len(transactions)}

Spending by Category:
{category_text}

Top 5 Largest Expenses:
{top_expenses_text}

{comparison_text}

Write the report in these sections:
1. **Overview** — 2-3 sentences on the overall financial health this month
2. **Where the money went** — highlight the top 2-3 spending categories and what they mean
3. **Biggest expenses** — call out any notable single transactions
4. **Month-over-Month** — only include this section if comparison data exists
5. **3 Actionable Suggestions** — specific, based on this person's actual data, not generic advice"""

    report_text = chat(SYSTEM_PROMPT, USER_PROMPT)

    return {
        "month": month or "Current Month",
        "currency": currency.value,
        "symbol": symbol,
        "summary": {
            "total_credits": round(total_credits, 2),
            "total_debits": round(total_debits, 2),
            "net": round(net, 2),
            "total_transactions": len(transactions),
            "savings_rate": round((net / total_credits * 100), 1) if total_credits > 0 else 0,
        },
        "category_breakdown": category_summary,
        "top_expenses": [
            {
                "date": t.date,
                "description": t.description,
                "amount": t.amount,
                "category": t.category.value if t.category else "Other"
            }
            for t in top_expenses
        ],
        "month_over_month": mom_data,
        "report": report_text,
    }
