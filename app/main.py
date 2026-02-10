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

def handle_intent(intent: str, data: dict) -> dict:
    """
    Deterministic core logic.
    """
    if intent == "QUERY_PILOTS":
        pilots = data["pilots"]
        available = pilots[
            pilots["status"]
            .fillna("")
            .astype(str)
            .str.lower() == "available"
        ]

        return {
            "intent": intent,
            "count": len(available),
            "message": f"{len(available)} pilots are currently available."
        }

    if intent == "QUERY_DRONES":
        drones = data["drones"]
        available = drones[
            drones["status"]
            .fillna("")
            .astype(str)
            .str.lower() == "available"
        ]

        return {
            "intent": intent,
            "count": len(available),
            "message": f"{len(available)} drones are currently available."
        }
    if pilots.empty:
        return {
            "intent": intent,
            "message": "No pilot data available from the roster."
        }

    return {
        "intent": intent,
        "message": f"Intent detected: {intent}"
    }

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Core conversational endpoint.
    Deterministic logic first, LLM for explanation.
    """
    data = load_all_data()
    intent = route_intent(req.message)

    # Deterministic result
    result = handle_intent(intent, data)

    # LLM explanation layer
    response = llm_response(req.message, result)

    return {"reply": response}


@app.get("/")
def root():
    return {"message": "Drone Ops AI is running"}

@app.get("/chat")
def chat_info():
    return {
        "info": "POST a JSON body like { 'message': '...' } to this endpoint"
    }
