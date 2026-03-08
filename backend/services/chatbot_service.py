import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def parse_query(user_query: str, persons: list) -> dict:
    """
    Call the Groq REST API directly (no SDK) to parse a natural-language
    photo query into a structured intent dict.

    Returns one of:
        {"intent": "search_person", "person_id": <int>}
        {"intent": "search_date",   "date": "YYYY-MM-DD"}
        {"intent": "search_all"}
        {"intent": "unknown"}
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to backend/.env and restart the server."
        )

    persons_str = (
        "\n".join(f"  - id={p['id']}, name={p['name']!r}" for p in persons)
        if persons
        else "  (no persons in the database yet)"
    )

    prompt = f"""You are an assistant for a photo management app called Drishyamitra.
Convert the user's request into a structured JSON command.

Known persons in the database:
{persons_str}

Possible intents:
1. search_person   — user wants photos of a specific person (optionally filtered by time)
2. search_date     — user wants photos from a specific date or relative time ("yesterday", "today", etc.) with NO specific person
3. search_all      — user wants to see all photos
4. send_email      — user wants to send photos to an email address
5. send_whatsapp   — user wants to send photos to a WhatsApp number
6. unknown         — query is unclear or unrelated to photos

Rules:
- For search_person,  output the person_id (integer) from the list above.
  If the user also mentions a time range, add "date_filter": one of "today", "yesterday", "last_week", "last_month".
  If no time range is mentioned, omit "date_filter".
- For search_date,    output the ISO date string (YYYY-MM-DD). Today is {_today()}.
- For send_email,     output the person_id (integer) and the email address as a string.
- For send_whatsapp,  output the person_id (integer) and the phone number in E.164 format (e.g. "+919876543210").
- Output ONLY a valid JSON object, no extra text, no markdown fences.

Examples:
  User: "Show photos of Mom" → {{"intent": "search_person", "person_id": 2}}
  User: "Show photos of Mom from yesterday" → {{"intent": "search_person", "person_id": 2, "date_filter": "yesterday"}}
  User: "Show photos of Mom last week" → {{"intent": "search_person", "person_id": 2, "date_filter": "last_week"}}
  User: "Show photos of Mom from last month" → {{"intent": "search_person", "person_id": 2, "date_filter": "last_month"}}
  User: "Show me photos from yesterday" → {{"intent": "search_date", "date": "{_yesterday()}"}}
  User: "Show all photos" → {{"intent": "search_all"}}
  User: "Send Person 2 photos to alice@gmail.com" → {{"intent": "send_email", "person_id": 2, "email": "alice@gmail.com"}}
  User: "Send Mom photos to WhatsApp +919876543210" → {{"intent": "send_whatsapp", "person_id": 2, "phone": "+919876543210"}}
  User: "What's the weather?" → {{"intent": "unknown"}}

User query: {user_query}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.0,
    }

    raw = ""
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        raw = data["choices"][0]["message"]["content"].strip()
        logger.debug("Groq raw response: %s", raw)

        # Safely extract the JSON object even if the model adds surrounding prose
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            logger.warning("No JSON object in Groq response: %s", raw)
            return {"intent": "unknown"}

        parsed = json.loads(raw[start:end])
        return parsed if "intent" in parsed else {"intent": "unknown"}

    except requests.HTTPError as exc:
        logger.error("Groq HTTP error %s: %s", exc.response.status_code, exc.response.text)
        raise
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error: %s — raw=%s", exc, raw)
        return {"intent": "unknown"}
    except Exception as exc:
        logger.error("Groq request error: %s", exc)
        raise


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _yesterday() -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=1)).isoformat()
