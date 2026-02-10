import json, random
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from rooms import rooms, create_room, ROLES
from game_logic import judge_teams

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

with open("characters.json") as f:
    CHARACTERS = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

# ---------- ROOM ----------

@app.route("/api/room/create", methods=["POST"])
def create():
    return jsonify({"room_id": create_room()})

@app.route("/api/room/join/<rid>", methods=["POST"])
def join(rid):
    room = rooms.get(rid)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    if not room["players"]["A"]:
        room["players"]["A"] = True
        return jsonify({"team": "A"})

    if not room["players"]["B"]:
        room["players"]["B"] = True
        room["current_team"] = "A"
        return jsonify({"team": "B"})

    return jsonify({"error": "Room full"}), 403

@app.route("/api/state/<rid>/<team>")
def state(rid, team):
    room = rooms[rid]
    joined = sum(room["players"].values())

    if joined < 2:
        phase = "WAITING"
    elif all(room["teams"]["A"]) and all(room["teams"]["B"]):
        phase = "SWAP" if (room["skips"]["A"] > 0 or room["skips"]["B"] > 0) else "RESULT"
    else:
        phase = "DRAFT"

    return jsonify({
        "phase": phase,
        "players_joined": joined,
        "your_turn": room["current_team"] == team and phase == "DRAFT",
        "pending_draw": room["pending_draw"] is not None,
        "your_team": room["teams"][team],
        "skips": room["skips"][team]
    })

# ---------- DRAFT ----------

@app.route("/api/draw/<rid>/<team>")
def draw(rid, team):
    room = rooms[rid]

    if room["current_team"] != team:
        return jsonify({"error": "Not your turn"}), 403
    if room["pending_draw"]:
        return jsonify({"error": "Assign first"}), 403

    available = [c for c in CHARACTERS if c["name"] not in room["used"]]
    room["pending_draw"] = random.choice(available)
    return jsonify({"name": room["pending_draw"]["name"]})

@app.route("/api/assign/<rid>", methods=["POST"])
def assign(rid):
    room = rooms[rid]
    data = request.json
    team = data["team"]
    slot = data["slot"]

    if room["current_team"] != team:
        return jsonify({"error": "Not your turn"}), 403
    if room["pending_draw"] is None:
        return jsonify({"error": "No draw"}), 400
    if room["teams"][team][slot] is not None:
        return jsonify({"error": "Slot filled"}), 400

    room["teams"][team][slot] = room["pending_draw"]
    room["used"].add(room["pending_draw"]["name"])
    room["pending_draw"] = None
    room["current_team"] = "B" if team == "A" else "A"

    return jsonify({"ok": True})

@app.route("/api/skip/<rid>/<team>", methods=["POST"])
def skip(rid, team):
    room = rooms[rid]
    if room["skips"][team] == 0:
        return jsonify({"error": "Skip used"}), 403
    room["skips"][team] -= 1
    room["pending_draw"] = None
    return jsonify({"ok": True})

@app.route("/api/swap/confirm/<rid>/<team>", methods=["POST"])
def confirm_swap(rid, team):
    room = rooms[rid]

    # Allow swap only if skip unused
    if room["skips"][team] == 0:
        return jsonify({"error": "No swap available"}), 403

    room["skips"][team] = 0  # consume swap
    room["swap_used"][team] = True

    return jsonify({"ok": True})

@app.route("/api/swap/<rid>", methods=["POST"])
def swap_roles(rid):
    room = rooms[rid]
    data = request.json
    team = data["team"]
    a = data["from"]
    b = data["to"]

    # Validation
    if room["skips"][team] == 0:
        return jsonify({"error": "Swap not available"}), 403

    if a == b:
        return jsonify({"error": "Choose two different slots"}), 400

    if room["teams"][team][a] is None or room["teams"][team][b] is None:
        return jsonify({"error": "Cannot swap empty slot"}), 400

    # 🔁 Perform swap
    room["teams"][team][a], room["teams"][team][b] = (
        room["teams"][team][b],
        room["teams"][team][a]
    )

    # Consume swap
    room["skips"][team] = 0
    room["swap_used"][team] = True

    return jsonify({"ok": True})

@app.route("/api/result/<rid>")
def result(rid):
    room = rooms[rid]
    return jsonify(judge_teams(room["teams"]["A"], room["teams"]["B"]))

if __name__ == "__main__":
    app.run(debug=True)