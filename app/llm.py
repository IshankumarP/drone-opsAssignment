import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def llm_response(user_message: str, system_result: dict) -> str:
    """
    Uses OpenAI for natural explanation.
    Falls back to deterministic response if unavailable.
    """
    if not OPENAI_API_KEY:
        return fallback_response(system_result)

    try:
        openai.api_key = OPENAI_API_KEY

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a drone operations coordinator assistant."},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": str(system_result)}
            ],
            max_tokens=150
        )

        return completion.choices[0].message["content"]

    except Exception:
        return fallback_response(system_result)


def fallback_response(system_result: dict) -> str:
    return f"[Fallback mode]\n{system_result.get('message', 'Request processed.')}"
