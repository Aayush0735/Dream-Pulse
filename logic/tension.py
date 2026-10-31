"""Tension scoring per ball, key moments, and smoothing."""
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.chase import chase_meter, projected_score


def get_phase(over):
    """Return phase label and multiplier for given over (0-based)."""
    if over <= 5:
        return "Powerplay", config.PHASE_MULT["powerplay"]
    elif over <= 14:
        return "Middle", config.PHASE_MULT["middle"]
    else:
        return "Death", config.PHASE_MULT["death"]


def event_points(ball):
    """Calculate event points for a delivery."""
    if ball["is_wicket"]:
        return config.EVENT_PTS["wicket"]
    if ball["runs_batter"] == 6:
        return config.EVENT_PTS["six"]
    if ball["runs_batter"] == 4:
        return config.EVENT_PTS["four"]
    if ball["runs_total"] == 0 and ball["legal"]:
        return config.EVENT_PTS["dot"]
    if not ball["legal"]:
        return config.EVENT_PTS["wide_noball"]
    return config.EVENT_PTS["other"]


def compute_chase_values(balls):
    """Compute chase meter values for all balls."""
    chase_values = []
    for b in balls:
        if b["innings"] == 2:
            cv = chase_meter(b["runs_needed"], b["balls_left"], b["wkts_in_hand"])
            chase_values.append(cv)
        else:
            chase_values.append(None)
    return chase_values


def compute_tension(balls, favourite_player=None):
    """
    Compute tension score for every ball.
    Returns list of dicts with tension info.
    """
    # First compute chase values
    chase_values = compute_chase_values(balls)

    # Compute raw tension for each ball
    raw_tensions = []
    for i, b in enumerate(balls):
        innings = b["innings"]
        over = b["over"]
        _, phase_mult = get_phase(over)
        evt_pts = event_points(b)

        # Swing (chase probability change)
        if innings == 2 and chase_values[i] is not None:
            if i > 0 and chase_values[i - 1] is not None:
                chase_before = chase_values[i - 1]
            else:
                # First ball of innings 2 - initial chase before ball 1
                chase_before = chase_meter(b.get("target", 0), 120, 10)
            chase_after = chase_values[i]
            swing = abs(chase_after - chase_before) * 100
            closeness = (1 - abs(chase_after - 0.5) * 2) * config.CLOSENESS_WEIGHT
            closeness = max(0, closeness)
        else:
            swing = 0
            closeness = 0
            chase_after = None

        raw = config.TENSION_SWING_WEIGHT * swing + evt_pts * phase_mult + closeness
        raw_tensions.append(raw)

    # Compute P95 for normalization
    if raw_tensions:
        p95 = np.percentile(raw_tensions, 95)
    else:
        p95 = 1.0
    if p95 == 0:
        p95 = 1.0

    # Normalize and add star bonus
    tensions = []
    for i, b in enumerate(balls):
        normalized = min(100, max(0, 100 * raw_tensions[i] / p95))

        # Star bonus
        star_bonus = 0
        if favourite_player:
            if (b["batter"] == favourite_player or
                b["bowler"] == favourite_player or
                b.get("player_out", "") == favourite_player):
                star_bonus = config.STAR_BONUS

        tension = min(100, normalized + star_bonus)

        tensions.append({
            "ball_idx": b["ball_idx"],
            "tension": tension,
            "raw": raw_tensions[i],
            "chase": chase_values[i],
            "swing": (
                abs(
                    chase_values[i]
                    - (
                        chase_values[i - 1]
                        if i > 0 and chase_values[i - 1] is not None
                        else chase_meter(b.get("target", 0), 120, 10)
                    )
                )
                * 100
                if chase_values[i] is not None
                else 0
            ),
            "event_pts": event_points(b),
            "phase": get_phase(b["over"])[0],
        })

    return tensions


def smooth_tension(tensions, window=None):
    """Apply rolling mean smoothing to tension values."""
    if window is None:
        window = config.TENSION_SMOOTH_WINDOW
    values = [t["tension"] for t in tensions]
    if len(values) < window:
        return values
    smoothed = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        smoothed.append(np.mean(values[start:i + 1]))
    return smoothed


def find_key_moments(tensions, balls, count=None, min_gap=None):
    """
    Find top N local maxima of tension, spaced at least min_gap balls apart.
    Returns list of dicts.
    """
    if count is None:
        count = config.TOP_MOMENTS_COUNT
    if min_gap is None:
        min_gap = config.MOMENTS_MIN_GAP

    # Find local maxima
    values = [t["tension"] for t in tensions]
    candidates = []
    for i in range(len(values)):
        is_max = True
        for j in range(max(0, i - 2), min(len(values), i + 3)):
            if j != i and values[j] > values[i]:
                is_max = False
                break
        if is_max:
            candidates.append((i, values[i]))

    # Sort by tension descending
    candidates.sort(key=lambda x: -x[1])

    # Pick top N with min_gap spacing
    selected = []
    for idx, tension_val in candidates:
        if len(selected) >= count:
            break
        # Check gap from already selected
        too_close = False
        for sel_idx, _ in selected:
            if abs(idx - sel_idx) < min_gap:
                too_close = True
                break
        if not too_close:
            b = balls[idx]
            # Determine reason
            if b["is_wicket"]:
                reason = f"Wicket! {b['player_out']} out ({b['wicket_kind']})"
            elif b["runs_batter"] == 6:
                reason = f"SIX by {b['batter']}!"
            elif b["runs_batter"] == 4:
                reason = f"FOUR by {b['batter']}!"
            elif b["innings"] == 2 and tension_val > 70:
                reason = f"Chase drama! {b['team_batting']} need {b['runs_needed']} off {b['balls_left']}"
            else:
                reason = f"High tension moment at {b['display_over']}"

            selected.append((idx, tension_val))

    # Sort by ball_idx for display
    selected.sort(key=lambda x: x[0])

    moments = []
    for rank, (idx, tension_val) in enumerate(selected, 1):
        b = balls[idx]
        if b["is_wicket"]:
            reason = f"Wicket! {b['player_out']} out ({b['wicket_kind']})"
        elif b["runs_batter"] == 6:
            reason = f"SIX by {b['batter']}!"
        elif b["runs_batter"] == 4:
            reason = f"FOUR by {b['batter']}!"
        elif b["innings"] == 2 and tension_val > 70:
            reason = f"Chase drama! {b['team_batting']} need {b['runs_needed']} off {b['balls_left']}"
        else:
            reason = f"High tension moment at {b['display_over']}"

        moments.append({
            "rank": rank,
            "ball_idx": idx,
            "display_over": b["display_over"],
            "innings": b["innings"],
            "tension": round(tension_val, 1),
            "reason": reason,
            "team_batting": b["team_batting"],
            "score": f"{b['cum_runs']}/{b['cum_wkts']}",
        })

    return moments

