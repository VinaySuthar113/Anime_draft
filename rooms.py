import uuid

ROLES = ["captain", "vice_captain", "tank", "healer", "support", "support"]

rooms = {}

def create_room():
    rid = str(uuid.uuid4())[:6].upper()
    rooms[rid] = {
        "players": {"A": False, "B": False},
        "current_team": "A",
        "teams": {
            "A": [None] * 6,
            "B": [None] * 6
        },
        "used": set(),
        "pending_draw": None,
        "skips": {"A": 1, "B": 1},
        "swap_used": {"A": False, "B": False}
    }
    return rid