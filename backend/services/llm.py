import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama3-70b-8192"


def chat(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Core LLM call. Swappable — replace Groq client with OpenAI/Anthropic here.
    json_mode=True enforces JSON output from the model.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def chat_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Convenience wrapper — returns parsed dict directly.
    Strips markdown fences if model adds them.
    """
    raw = chat(system_prompt, user_prompt, json_mode=True)

    # Strip markdown fences if present
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\nRaw output: {raw}")
