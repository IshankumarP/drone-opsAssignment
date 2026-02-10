def route_intent(message: str) -> str:
    msg = message.lower()

    if "available pilot" in msg or "available pilots" in msg:
        return "QUERY_PILOTS"

    if "assign" in msg:
        return "ASSIGN_MISSION"

    if "update pilot" in msg or "set pilot" in msg:
        return "UPDATE_PILOT_STATUS"

    if "conflict" in msg:
        return "CHECK_CONFLICTS"

    if "urgent" in msg or "reassign" in msg:
        return "URGENT_REASSIGNMENT"

    return "GENERAL_QUERY"
