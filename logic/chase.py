"""Chase meter calculation (second innings) and projected score (first innings)."""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def chase_meter(runs_needed, balls_left, wkts_in_hand):
    """
    Compute chase probability for batting team in second innings.
    Returns float in [0.0, 1.0].
    """
    # Chase complete
    if runs_needed <= 0:
        return 1.0
    # All out or no balls left
    if wkts_in_hand <= 0 or balls_left <= 0:
        return 0.0

    rrr = runs_needed * 6 / balls_left
    par = config.CHASE_PAR_BASE * (
        config.CHASE_PAR_CONST
        + config.CHASE_PAR_WKT_WEIGHT * (wkts_in_hand / 10) ** config.CHASE_PAR_EXP
    )
    pressure = rrr - par
    chase = 1.0 / (1.0 + math.exp(config.CHASE_SLOPE * pressure))
    return max(config.CHASE_MIN, min(config.CHASE_MAX, chase))


def projected_score(cum_runs, balls_left, legal_balls_bowled):
    """
    Projected score for first innings.
    Returns int.
    """
    if legal_balls_bowled == 0:
        current_rpb = config.PROJ_AVG_RPB
    else:
        current_rpb = cum_runs / legal_balls_bowled

    proj = cum_runs + balls_left * (
        config.PROJ_CRR_WEIGHT * current_rpb
        + (1 - config.PROJ_CRR_WEIGHT) * config.PROJ_AVG_RPB
    )
    return round(proj)

