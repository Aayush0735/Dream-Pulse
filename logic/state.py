"""State snapshot at any ball index."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.chase import chase_meter, projected_score
from logic.tension import get_phase


def state_at(ball_idx, balls, tensions=None, moments=None):
    """
    Build complete state snapshot at a given ball index.
    Returns dict with all relevant match info.
    """
    if ball_idx < 0 or ball_idx >= len(balls):
        return None

    b = balls[ball_idx]
    innings = b["innings"]

    # Current batters: find who's at the crease
    current_batters = []
    dismissed = set()
    batter_stats = {}  # name -> {runs, balls}

    for i in range(ball_idx + 1):
        bi = balls[i]
        if bi["innings"] != innings:
            continue
        # Track batter stats
        batter = bi["batter"]
        if batter not in batter_stats:
            batter_stats[batter] = {"runs": 0, "balls": 0}
        batter_stats[batter]["runs"] += bi["runs_batter"]
        if bi["legal"]:
            batter_stats[batter]["balls"] += 1
        # Track dismissals
        if bi["is_wicket"]:
            dismissed.add(bi["player_out"])

    # Current batters are those who have batted but not dismissed
    for name, stats in batter_stats.items():
        if name not in dismissed:
            current_batters.append({
                "name": name,
                "runs": stats["runs"],
                "balls": stats["balls"]
            })

    # Keep only the last 2 batters who appeared
    if len(current_batters) > 2:
        # Sort by last appearance
        last_app = {}
        for i in range(ball_idx + 1):
            bi = balls[i]
            if bi["innings"] == innings:
                last_app[bi["batter"]] = i
                last_app[bi["non_striker"]] = i
        current_batters.sort(key=lambda x: last_app.get(x["name"], 0), reverse=True)
        current_batters = current_batters[:2]

    # Current bowler figures
    bowler = b["bowler"]
    bowler_stats = {"name": bowler, "overs": 0, "runs": 0, "wickets": 0, "legal_balls": 0}
    for i in range(ball_idx + 1):
        bi = balls[i]
        if bi["innings"] == innings and bi["bowler"] == bowler:
            bowler_stats["runs"] += bi["runs_total"]
            if bi["is_wicket"]:
                bowler_stats["wickets"] += 1
            if bi["legal"]:
                bowler_stats["legal_balls"] += 1
    bowler_stats["overs"] = f"{bowler_stats['legal_balls'] // 6}.{bowler_stats['legal_balls'] % 6}"

    # Last 12 balls
    last_12 = []
    count = 0
    for i in range(ball_idx, -1, -1):
        bi = balls[i]
        if bi["innings"] == innings:
            if bi["is_wicket"]:
                last_12.insert(0, "W")
            elif not bi["legal"]:
                last_12.insert(0, "•")
            else:
                last_12.insert(0, str(bi["runs_total"]))
            count += 1
            if count >= 12:
                break

    # Current partnership
    partnership = {"runs": 0, "balls": 0}
    # Go back from current ball to find last wicket
    last_wkt_idx = -1
    for i in range(ball_idx, -1, -1):
        bi = balls[i]
        if bi["innings"] == innings and bi["is_wicket"] and i < ball_idx:
            last_wkt_idx = i
            break

    for i in range(last_wkt_idx + 1, ball_idx + 1):
        bi = balls[i]
        if bi["innings"] == innings:
            partnership["runs"] += bi["runs_total"]
            if bi["legal"]:
                partnership["balls"] += 1

    # Chase meter or projected score
    if innings == 2:
        cm = chase_meter(b["runs_needed"], b["balls_left"], b["wkts_in_hand"])
        proj = None
    else:
        cm = None
        proj = projected_score(b["cum_runs"], b["balls_left"], b["legal_balls_bowled"])

    # Run rates
    if b["legal_balls_bowled"] > 0:
        crr = round(b["cum_runs"] * 6 / b["legal_balls_bowled"], 2)
    else:
        crr = 0.0

    if innings == 2 and b["balls_left"] > 0:
        rrr = round(b["runs_needed"] * 6 / b["balls_left"], 2)
    else:
        rrr = None

    # Phase
    phase_label, _ = get_phase(b["over"])

    # What next
    balls_in_pp = max(0, 36 - b["legal_balls_bowled"]) if innings == 1 else max(0, 36 - (b["legal_balls_bowled"] - sum(1 for x in balls if x["innings"] == 1 and x["legal"])))
    if b["innings"] == 2:
        inn2_legal = sum(1 for x in balls[:ball_idx+1] if x["innings"] == 2 and x["legal"])
        balls_in_pp = max(0, 36 - inn2_legal)

    if phase_label == "Powerplay" and balls_in_pp > 0:
        what_next = f"Powerplay ends in {balls_in_pp} balls"
    elif innings == 2 and b["balls_left"] <= 12:
        what_next = f"Last 2 overs! {b['runs_needed']} needed off {b['balls_left']}"
    elif innings == 2 and b["balls_left"] <= 30:
        what_next = f"Death overs approaching. {b['runs_needed']} needed"
    else:
        what_next = f"{phase_label} phase"

    # Key moments so far
    moments_so_far = []
    if moments:
        moments_so_far = [m for m in moments if m["ball_idx"] <= ball_idx]

    state = {
        "ball_idx": ball_idx,
        "innings": innings,
        "team_batting": b["team_batting"],
        "score": b["cum_runs"],
        "wickets": b["cum_wkts"],
        "overs": b["display_over"],
        "target": b["target"] if innings == 2 else None,
        "runs_needed": b["runs_needed"] if innings == 2 else None,
        "balls_left": b["balls_left"],
        "wkts_in_hand": b["wkts_in_hand"],
        "rrr": rrr,
        "crr": crr,
        "chase_meter": round(cm * 100, 1) if cm is not None else None,
        "projected_score": proj,
        "current_batters": current_batters,
        "current_bowler": bowler_stats,
        "last_12": last_12,
        "partnership": partnership,
        "key_moments": moments_so_far,
        "phase": phase_label,
        "what_next": what_next,
    }

    return state

