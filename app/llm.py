import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_response(user_message: str, result: dict) -> str:
    """
    LLM layer that explains deterministic results.
    Never makes decisions.
    """
    system_prompt = """
You are a Drone Operations Coordinator AI.
Explain results clearly and concisely.
Do NOT invent data.
Use the provided result only.
"""

    prompt = f"""
User asked: {user_message}

System result:
{result}

Explain this to the user in a helpful, operational tone.
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content
    except Exception:
        # Hard safety fallback
        return result.get("message", "Unable to generate response.")
