from fastapi import FastAPI
from pydantic import BaseModel
from app.intent_router import route_intent
from dotenv import load_dotenv
from app.llm import llm_response
from app.sheets import load_all_data

load_dotenv()

app = FastAPI(title="Drone Ops Coordinator AI")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Core conversational endpoint.
    Deterministic logic first, LLM for explanation.
    """
    data = load_all_data()
    intent = route_intent(req.message)

    # Placeholder result (will expand)
    result = {
        "intent": intent,
        "message": f"Intent detected: {intent}"
    }

    # LLM explanation layer (safe fallback)
    response = llm_response(req.message, result)
    return {"reply": response}
