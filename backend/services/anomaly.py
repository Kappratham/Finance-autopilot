import statistics
from services.llm import chat_json
from models.schemas import Transaction, Currency


def detect_anomalies(transactions: list[Transaction]) -> dict:
    """
    Two-layer anomaly detection:
    1. Statistical — flags transactions 2x above category average
    2. LLM — explains why each flagged transaction is unusual in plain English
    """
    if not transactions:
        return {"anomalies": [], "summary": "No transactions to analyze."}

    currency = transactions[0].currency
    symbol = "₹" if currency == Currency.INR else "$"

    # --- Layer 1: Statistical Detection ---
    # Group debits by category
    category_amounts: dict[str, list[float]] = {}
    for t in transactions:
        if t.type == "debit" and t.category:
            cat = t.category.value
            if cat not in category_amounts:
                category_amounts[cat] = []
            category_amounts[cat].append(t.amount)

    # Calculate mean + std per category
    category_stats = {}
    for cat, amounts in category_amounts.items():
        if len(amounts) >= 2:
            mean = statistics.mean(amounts)
            std = statistics.stdev(amounts)
            category_stats[cat] = {"mean": mean, "std": std, "threshold": mean + (2 * std)}
        else:
            # Only one transaction in category — use 2x as threshold
            category_stats[cat] = {"mean": amounts[0], "std": 0, "threshold": amounts[0] * 2}

    # Flag anomalies
    flagged = []
    for t in transactions:
        if t.type != "debit" or not t.category:
            continue
        cat = t.category.value
        if cat in category_stats:
            stats = category_stats[cat]
            if t.amount > stats["threshold"] and t.amount > 100:  # ignore tiny amounts
                flagged.append({
                    "transaction": t,
                    "category_mean": round(stats["mean"], 2),
                    "threshold": round(stats["threshold"], 2),
                    "deviation": round(((t.amount - stats["mean"]) / stats["mean"]) * 100, 1)
                })

    # Also flag duplicate descriptions on same day
    seen = {}
    for t in transactions:
        key = f"{t.date}_{t.description.lower()[:20]}"
        if key in seen:
            # potential duplicate
            flagged.append({
                "transaction": t,
                "category_mean": t.amount,
                "threshold": t.amount,
                "deviation": 0,
                "is_duplicate": True
            })
        seen[key] = t

    if not flagged:
        return {
            "anomalies": [],
            "total_flagged": 0,
            "summary": "No unusual transactions detected. Your spending looks consistent this month."
        }

    # --- Layer 2: LLM Explanation ---
    flagged_text = "\n".join([
        f"- {f['transaction'].date}: {f['transaction'].description} — {symbol}{f['transaction'].amount:,.2f} "
        f"(category avg: {symbol}{f['category_mean']:,.2f}, {f['deviation']:+.0f}% above normal)"
        + (" [POSSIBLE DUPLICATE]" if f.get("is_duplicate") else "")
        for f in flagged
    ])

    SYSTEM_PROMPT = """You are a personal finance analyst detecting unusual spending.
For each flagged transaction, give a brief, plain English explanation of why it's unusual.
Be specific and practical. Don't be alarmist — just helpful.
Return only valid JSON."""

    USER_PROMPT = f"""These transactions were flagged as unusual compared to this person's normal spending patterns.
Explain each one briefly and suggest if action is needed.

Flagged transactions:
{flagged_text}

Return this exact JSON structure:
{{
  "explanations": [
    {{
      "description": "transaction description",
      "amount": 0.00,
      "reason": "plain English reason why this is unusual",
      "action_needed": true or false,
      "suggestion": "what to do about it, or null if no action needed"
    }}
  ],
  "overall_summary": "1-2 sentence summary of the anomaly findings"
}}"""

    try:
        llm_result = chat_json(SYSTEM_PROMPT, USER_PROMPT)
        explanations = llm_result.get("explanations", [])
        overall_summary = llm_result.get("overall_summary", "")
    except Exception:
        explanations = []
        overall_summary = f"{len(flagged)} unusual transactions detected."

    # Merge statistical + LLM results
    anomalies = []
    for i, f in enumerate(flagged):
        t = f["transaction"]
        explanation = explanations[i] if i < len(explanations) else {}
        anomalies.append({
            "date": t.date,
            "description": t.description,
            "amount": t.amount,
            "category": t.category.value if t.category else "Other",
            "currency": currency.value,
            "category_average": f["category_mean"],
            "deviation_percent": f["deviation"],
            "is_duplicate": f.get("is_duplicate", False),
            "reason": explanation.get("reason", "Significantly above your normal spending for this category."),
            "action_needed": explanation.get("action_needed", False),
            "suggestion": explanation.get("suggestion"),
        })

    return {
        "anomalies": anomalies,
        "total_flagged": len(anomalies),
        "summary": overall_summary,
        "category_stats": {
            cat: {"mean": round(s["mean"], 2), "threshold": round(s["threshold"], 2)}
            for cat, s in category_stats.items()
        }
    }
