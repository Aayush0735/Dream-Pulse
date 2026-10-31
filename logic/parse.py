"""
Parse Cricsheet JSON into balls.csv.
Also provides a synthetic match generator as fallback.
"""
import json
import csv
import os
import sys
import numpy as np

# Add parent to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def generate_synthetic_match(seed=42):
    """Generate a synthetic IND vs PAK T20 chase (close finish) in Cricsheet JSON format."""
    rng = np.random.RandomState(seed)

    teams = ["India", "Pakistan"]
    india_batters = [
        "KL Rahul", "Rohit Sharma", "Virat Kohli", "Suryakumar Yadav",
        "Hardik Pandya", "Dinesh Karthik", "Axar Patel", "Ravichandran Ashwin",
        "Bhuvneshwar Kumar", "Mohammed Shami", "Arshdeep Singh"
    ]
    india_bowlers = ["Bhuvneshwar Kumar", "Arshdeep Singh", "Mohammed Shami",
                     "Hardik Pandya", "Axar Patel", "Ravichandran Ashwin"]
    pak_batters = [
        "Babar Azam", "Mohammad Rizwan", "Shan Masood", "Iftikhar Ahmed",
        "Shadab Khan", "Mohammad Nawaz", "Asif Ali", "Shaheen Afridi",
        "Haris Rauf", "Naseem Shah", "Mohammad Wasim"
    ]
    pak_bowlers = ["Shaheen Afridi", "Haris Rauf", "Naseem Shah",
                   "Mohammad Nawaz", "Shadab Khan", "Mohammad Wasim"]

    def simulate_innings(batters, bowlers, target=None):
        """Simulate a T20 innings."""
        overs_data = []
        batter_idx = 0
        on_strike = batters[0]
        non_strike = batters[1]
        batter_idx = 2
        total_runs = 0
        wickets = 0
        legal_balls = 0

        for over_num in range(20):
            bowler = bowlers[over_num % len(bowlers)]
            deliveries = []
            balls_in_over = 0

            while balls_in_over < 6:
                if wickets >= 10:
                    break
                if target and total_runs >= target:
                    break

                delivery = {
                    "batter": on_strike,
                    "bowler": bowler,
                    "non_striker": non_strike,
                    "runs": {"batter": 0, "extras": 0, "total": 0}
                }

                # Determine outcome with phase-aware probabilities
                r = rng.random()
                is_death = over_num >= 15
                is_powerplay = over_num < 6

                if r < 0.03 and not (target and total_runs >= target - 10):
                    # Wide
                    delivery["runs"] = {"batter": 0, "extras": 1, "total": 1}
                    delivery["extras"] = {"wides": 1}
                    total_runs += 1
                    deliveries.append(delivery)
                    continue
                elif r < 0.05:
                    # No ball
                    nb_runs = rng.choice([0, 1, 4, 6], p=[0.5, 0.2, 0.2, 0.1])
                    delivery["runs"] = {"batter": nb_runs, "extras": 1, "total": nb_runs + 1}
                    delivery["extras"] = {"noballs": 1}
                    total_runs += nb_runs + 1
                    if nb_runs % 2 == 1:
                        on_strike, non_strike = non_strike, on_strike
                    deliveries.append(delivery)
                    continue

                balls_in_over += 1
                legal_balls += 1

                # Adjust probabilities for close finish
                wicket_prob = 0.05 if not is_death else 0.07
                six_prob = 0.08 if is_death else 0.05
                four_prob = 0.12 if is_powerplay else 0.10
                dot_prob = 0.35

                if target and total_runs >= target - 20 and is_death:
                    six_prob = 0.12
                    four_prob = 0.15
                    wicket_prob = 0.08

                if r < dot_prob:
                    runs = 0
                elif r < dot_prob + 0.20:
                    runs = 1
                elif r < dot_prob + 0.30:
                    runs = 2
                elif r < dot_prob + 0.33:
                    runs = 3
                elif r < dot_prob + 0.33 + four_prob:
                    runs = 4
                elif r < dot_prob + 0.33 + four_prob + six_prob:
                    runs = 6
                else:
                    # Wicket
                    if rng.random() < wicket_prob * 3:
                        runs = 0
                        wicket_kinds = ["bowled", "caught", "lbw", "caught and bowled", "stumped"]
                        delivery["wickets"] = [{
                            "player_out": on_strike,
                            "kind": rng.choice(wicket_kinds)
                        }]
                        wickets += 1
                        if batter_idx < len(batters):
                            on_strike = batters[batter_idx]
                            batter_idx += 1
                    else:
                        runs = rng.choice([0, 1, 2])

                delivery["runs"] = {"batter": runs, "extras": 0, "total": runs}
                total_runs += runs
                if runs % 2 == 1:
                    on_strike, non_strike = non_strike, on_strike
                deliveries.append(delivery)

            if deliveries:
                overs_data.append({"over": over_num, "deliveries": deliveries})

            # Swap strike at end of over
            on_strike, non_strike = non_strike, on_strike

            if wickets >= 10:
                break
            if target and total_runs >= target:
                break

        return overs_data, total_runs, wickets

    # Pakistan bats first, scores 150-165
    pak_overs, pak_total, pak_wkts = simulate_innings(pak_batters, india_bowlers)

    # India chases - we want it close (within 5 runs, last 2 overs)
    # Regenerate until close
    for attempt in range(100):
        rng2 = np.random.RandomState(seed + attempt + 100)
        # Temporarily swap rng
        old_rng = rng
        rng = rng2
        ind_overs, ind_total, ind_wkts = simulate_innings(india_batters, pak_bowlers, target=pak_total + 1)
        rng = old_rng
        # Check if it's a close finish
        if abs(ind_total - pak_total) <= 10 and ind_total >= pak_total:
            break

    match_data = {
        "meta": {"data_version": "1.0.0", "created": "2022-10-23"},
        "info": {
            "balls_per_over": 6,
            "city": "Melbourne",
            "dates": ["2022-10-23"],
            "event": {"name": "ICC Men's T20 World Cup", "match_number": 16},
            "gender": "male",
            "match_type": "T20",
            "outcome": {
                "winner": "India" if ind_total > pak_total else "Pakistan",
                "by": {"wickets": 10 - ind_wkts} if ind_total > pak_total else {"runs": pak_total - ind_total}
            },
            "overs": 20,
            "teams": teams,
            "toss": {"decision": "bat", "winner": "Pakistan"},
            "venue": "Melbourne Cricket Ground"
        },
        "innings": [
            {"team": "Pakistan", "overs": pak_overs},
            {"team": "India", "overs": ind_overs}
        ]
    }

    return match_data


def parse_match_json(match_path):
    """Parse Cricsheet JSON into a list of ball dicts."""
    with open(match_path, 'r') as f:
        data = json.load(f)

    info = data.get("info", {})
    innings_data = data.get("innings", [])

    teams = info.get("teams", ["Team A", "Team B"])
    print(f"Match: {teams[0]} vs {teams[1]}")
    print(f"Date: {info.get('dates', ['Unknown'])[0]}")
    print(f"Venue: {info.get('venue', 'Unknown')}")
    if "event" in info:
        print(f"Event: {info['event'].get('name', '')} #{info['event'].get('match_number', '')}")
    if "outcome" in info:
        outcome = info["outcome"]
        if "winner" in outcome:
            by = outcome.get("by", {})
            by_str = ", ".join(f"{v} {k}" for k, v in by.items())
            print(f"Result: {outcome['winner']} won by {by_str}")

    balls = []
    ball_idx = 0

    for inn_num, innings in enumerate(innings_data, 1):
        team_batting = innings.get("team", f"Team {inn_num}")
        # Determine target for 2nd innings
        if inn_num == 2 and len(balls) > 0:
            inn1_total = sum(b["runs_total"] for b in balls if b["innings"] == 1)
            target = inn1_total + 1
        else:
            target = 0

        cum_runs = 0
        cum_wkts = 0
        legal_balls_bowled = 0

        for over_data in innings.get("overs", []):
            over_num = over_data["over"]  # 0-based

            for del_idx, delivery in enumerate(over_data.get("deliveries", [])):
                batter = delivery.get("batter", "")
                bowler = delivery.get("bowler", "")
                non_striker = delivery.get("non_striker", "")
                runs = delivery.get("runs", {})
                runs_batter = runs.get("batter", 0)
                runs_extras = runs.get("extras", 0)
                runs_total = runs.get("total", 0)

                # Determine if legal delivery
                extras = delivery.get("extras", {})
                is_wide = "wides" in extras
                is_noball = "noballs" in extras
                legal = not (is_wide or is_noball)

                # Wickets
                wickets = delivery.get("wickets", [])
                is_wicket = len(wickets) > 0
                wicket_kind = wickets[0]["kind"] if is_wicket else ""
                player_out = wickets[0]["player_out"] if is_wicket else ""

                cum_runs += runs_total
                if is_wicket:
                    cum_wkts += 1
                if legal:
                    legal_balls_bowled += 1

                # Calculate ball_in_over for display
                # Count legal balls in this over so far
                balls_in_this_over = sum(
                    1 for b in balls
                    if b["innings"] == inn_num and b["over"] == over_num and b["legal"]
                )
                if legal:
                    ball_display = balls_in_this_over + 1
                else:
                    ball_display = balls_in_this_over

                # Calculate derived fields
                if inn_num == 2 and target > 0:
                    runs_needed = target - cum_runs
                    # balls_left = total legal balls possible - legal balls bowled
                    balls_left = 120 - legal_balls_bowled
                    wkts_in_hand = 10 - cum_wkts
                else:
                    runs_needed = 0
                    total_legal_first = 120
                    balls_left = total_legal_first - legal_balls_bowled
                    wkts_in_hand = 10 - cum_wkts

                display_over = f"{over_num}.{ball_display}"

                ball = {
                    "ball_idx": ball_idx,
                    "innings": inn_num,
                    "over": over_num,
                    "ball_in_over": del_idx,
                    "legal": legal,
                    "batter": batter,
                    "non_striker": non_striker,
                    "bowler": bowler,
                    "runs_batter": runs_batter,
                    "runs_extras": runs_extras,
                    "runs_total": runs_total,
                    "is_wicket": is_wicket,
                    "wicket_kind": wicket_kind,
                    "player_out": player_out,
                    "team_batting": team_batting,
                    "cum_runs": cum_runs,
                    "cum_wkts": cum_wkts,
                    "legal_balls_bowled": legal_balls_bowled,
                    "target": target if inn_num == 2 else 0,
                    "runs_needed": runs_needed if inn_num == 2 else 0,
                    "balls_left": balls_left,
                    "wkts_in_hand": wkts_in_hand,
                    "display_over": display_over,
                }

                balls.append(ball)
                ball_idx += 1

    return balls, data


def save_balls_csv(balls, path):
    """Save balls list to CSV."""
    if not balls:
        return
    fieldnames = list(balls[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(balls)


def verify_totals(balls, match_data):
    """Verify that parsed totals match the match file."""
    innings_data = match_data.get("innings", [])
    all_ok = True

    for inn_num, innings in enumerate(innings_data, 1):
        inn_balls = [b for b in balls if b["innings"] == inn_num]
        if not inn_balls:
            continue

        parsed_total = inn_balls[-1]["cum_runs"]
        parsed_wkts = inn_balls[-1]["cum_wkts"]
        legal_count = sum(1 for b in inn_balls if b["legal"])

        team = innings.get("team", f"Team {inn_num}")
        print(f"\nInnings {inn_num} ({team}):")
        print(f"  Total: {parsed_total}/{parsed_wkts}")
        print(f"  Legal balls: {legal_count}")

        # Verify legal balls <= 120
        if legal_count > 120:
            print(f"  ERROR: Legal balls {legal_count} exceeds 120!")
            all_ok = False
        else:
            print(f"  OK: Legal balls within limit")

        # Cross-check with source data
        source_total = 0
        for over_data in innings.get("overs", []):
            for delivery in over_data.get("deliveries", []):
                source_total += delivery.get("runs", {}).get("total", 0)
        if source_total == parsed_total:
            print(f"  OK: Total matches source ({source_total})")
        else:
            print(f"  ERROR: Parsed total {parsed_total} != source {source_total}")
            all_ok = False

    return all_ok


def get_star_players(balls):
    """Get top 3 batters by runs and top 2 bowlers by wickets."""
    from collections import defaultdict

    batter_runs = defaultdict(int)
    bowler_wickets = defaultdict(int)

    for b in balls:
        batter_runs[b["batter"]] += b["runs_batter"]
        if b["is_wicket"]:
            bowler_wickets[b["bowler"]] += 1

    top_batters = sorted(batter_runs.items(), key=lambda x: -x[1])[:3]
    top_bowlers = sorted(bowler_wickets.items(), key=lambda x: -x[1])[:2]

    print("\nStar Players:")
    print("  Top Batters:")
    for name, runs in top_batters:
        print(f"    {name}: {runs} runs")
    print("  Top Bowlers:")
    for name, wkts in top_bowlers:
        print(f"    {name}: {wkts} wickets")

    return {
        "batters": [{"name": n, "runs": r} for n, r in top_batters],
        "bowlers": [{"name": n, "wickets": w} for n, w in top_bowlers],
    }


if __name__ == "__main__":
    import sys
    match_path = sys.argv[1] if len(sys.argv) > 1 else config.MATCH_JSON

    if not os.path.exists(match_path):
        print("Match file not found, generating synthetic match...")
        match_data = generate_synthetic_match()
        os.makedirs(os.path.dirname(match_path), exist_ok=True)
        with open(match_path, 'w') as f:
            json.dump(match_data, f, indent=2)
        print(f"Synthetic match saved to {match_path}")
    else:
        with open(match_path, 'r') as f:
            match_data = json.load(f)

    balls, data = parse_match_json(match_path)
    verify_totals(balls, data)
    get_star_players(balls)
    save_balls_csv(balls, config.BALLS_CSV)
    print(f"\nSaved {len(balls)} deliveries to {config.BALLS_CSV}")
