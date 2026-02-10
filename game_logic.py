ROLES = ["captain", "vice_captain", "tank", "healer", "support", "support"]

def judge_teams(teamA, teamB):
    rounds = []
    scoreA = scoreB = 0

    for i, role in enumerate(ROLES):
        a = teamA[i]
        b = teamB[i]

        pa = a["base_power"] + a["role_bonus"].get(role, 0)
        pb = b["base_power"] + b["role_bonus"].get(role, 0)

        if pa > pb:
            winner = "Team A"
            scoreA += 1
        elif pb > pa:
            winner = "Team B"
            scoreB += 1
        else:
            winner = "Draw"

        rounds.append({
            "role": role,
            "A": a["name"],
            "B": b["name"],
            "winner": winner
        })

    final = "Draw"
    if scoreA > scoreB:
        final = "Team A"
    elif scoreB > scoreA:
        final = "Team B"

    return {
        "rounds": rounds,
        "final_winner": final
    }