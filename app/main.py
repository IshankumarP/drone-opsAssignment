from fastapi import FastAPI
from pydantic import BaseModel
from app.intent_router import route_intent
from dotenv import load_dotenv
from app.llm import llm_response
from app.sheets import load_all_data
from datetime import datetime

def dates_overlap(start1, end1, start2, end2):
    return max(start1, end1) >= min(end2, start2)


load_dotenv()

app = FastAPI(title="Drone Ops Coordinator AI")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}


def check_conflicts(pilot, drone, mission, missions_df):
    conflicts = []

    # 1. Certification mismatch
    required_certs = set(mission["required_certs"].split(","))
    pilot_certs = set(pilot["certifications"].split(","))

    if not required_certs.issubset(pilot_certs):
        conflicts.append("Pilot lacks required certifications.")

    # 2. Drone maintenance
    if drone["status"].lower() == "maintenance":
        conflicts.append("Drone is currently under maintenance.")

    # 3. Location mismatch
    if pilot["location"] != drone["location"]:
        conflicts.append("Pilot and drone are in different locations.")

    # 4. Pilot double booking
    for _, m in missions_df.iterrows():
        if m["project_id"] == pilot["current_assignment"]:
            start1 = datetime.fromisoformat(m["start_date"])
            end1 = datetime.fromisoformat(m["end_date"])
            start2 = datetime.fromisoformat(mission["start_date"])
            end2 = datetime.fromisoformat(mission["end_date"])

            if dates_overlap(start1, end1, start2, end2):
                conflicts.append("Pilot is already assigned to an overlapping mission.")

    return conflicts

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
    if intent == "CHECK_CONFLICTS":
        missions = data["missions"]
        pilots = data["pilots"]
        drones = data["drones"]

    # Simple example: first pilot + first drone + first mission
        pilot = pilots.iloc[0]
        drone = drones.iloc[0]
        mission = missions.iloc[0]

        conflicts = check_conflicts(pilot, drone, mission, missions)

        if not conflicts:
            return {
                "intent": intent,
                "message": "No conflicts detected. Assignment is feasible."
            }

        return {
            "intent": intent,
            "conflicts": conflicts,
            "message": "Conflicts detected."
        }
    if intent == "URGENT_REASSIGNMENT":
        missions = data["missions"]
        pilots = data["pilots"]

        urgent = missions.sort_values("priority", ascending=False).iloc[0]
        available = pilots[pilots["status"].str.lower() == "available"]

        if available.empty:
            return {
                "intent": intent,
                "message": "No available pilots for urgent reassignment."
            }

        pilot = available.iloc[0]

        return {
            "intent": intent,
            "message": f"Pilot {pilot['name']} can be urgently reassigned to project {urgent['project_id']}."
        }


    if data.get("pilots") is None or data["pilots"].empty:
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
