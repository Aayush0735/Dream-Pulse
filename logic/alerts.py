"""Alert generation from tension data."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def determine_trigger(ball):
    """Determine what triggered the alert."""
    if ball["is_wicket"]:
        return "wicket"
    if ball["runs_batter"] == 6:
        return "six"
    if ball["runs_batter"] == 4:
        return "four"
    if ball["innings"] == 2 and ball["balls_left"] <= 18:
        return "close_finish"
    return "swing"


def determine_severity(tension):
    """Determine alert severity."""
    if tension >= config.ALERT_SEVERITY["Hot"]:
        return "Hot"
    elif tension >= config.ALERT_SEVERITY["Rising"]:
        return "Rising"
    return "Watch"


def build_facts(ball, tension_val, chase_val):
    """Build facts dict for alert."""
    facts = {
        "ball_idx": ball["ball_idx"],
        "display_over": ball["display_over"],
        "innings": ball["innings"],
        "team_batting": ball["team_batting"],
        "score": f"{ball['cum_runs']}/{ball['cum_wkts']}",
        "batter": ball["batter"],
        "bowler": ball["bowler"],
        "runs_total": ball["runs_total"],
        "tension": round(tension_val, 1),
    }
    if ball["is_wicket"]:
        facts["wicket"] = ball["player_out"]
        facts["wicket_kind"] = ball["wicket_kind"]
    if ball["runs_batter"] >= 4:
        facts["boundary"] = ball["runs_batter"]
    if ball["innings"] == 2:
        facts["runs_needed"] = ball["runs_needed"]
        facts["balls_left"] = ball["balls_left"]
        facts["wkts_in_hand"] = ball["wkts_in_hand"]
        if chase_val is not None:
            facts["chase_meter"] = round(chase_val * 100, 1)
    return facts


def generate_alerts(balls, tensions, sensitivity="Hyped"):
    """
    Generate alerts based on tension values and sensitivity threshold.
    Returns list of alert dicts.
    """
    threshold = config.SENSITIVITY.get(sensitivity, config.SENSITIVITY["Normal"])
    alerts = []
    last_alert_idx = -config.ALERT_GAP_NORMAL  # Allow first ball to trigger

    for i, ball in enumerate(balls):
        tension_val = tensions[i]["tension"]
        chase_val = tensions[i].get("chase")
        gap = i - last_alert_idx

        # Check if alert should fire
        should_fire = False
        if tension_val >= threshold and gap >= config.ALERT_GAP_NORMAL:
            should_fire = True
        elif tension_val >= config.ALERT_HIGH_TENSION and gap >= config.ALERT_GAP_HIGH:
            should_fire = True

        if should_fire:
            trigger = determine_trigger(ball)
            severity = determine_severity(tension_val)
            facts = build_facts(ball, tension_val, chase_val)

            alert = {
                "ball_idx": ball["ball_idx"],
                "display_over": ball["display_over"],
                "severity": severity,
                "trigger": trigger,
                "facts": facts,
                "tension": round(tension_val, 1),
                "innings": ball["innings"],
            }
            alerts.append(alert)
            last_alert_idx = i

    return alerts


def alerts_for_all_sensitivities(balls, tensions):
    """Generate alerts for all sensitivity levels. Returns dict keyed by sensitivity."""
    result = {}
    for sens in config.SENSITIVITY:
        result[sens] = generate_alerts(balls, tensions, sens)
    return result

