"""Template-based fallbacks for all AI features. No model needed."""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ── Chat templates ────────────────────────────────────────────

HANDLES = [
    "CricFan_99", "BleedBlue_07", "SixerKing", "PakZindabad", "BollywoodBatter",
    "DelhiDynamo", "KarachiKid", "MumbaiMagic", "GullyBoy", "ChaiAndCricket",
    "ViratArmy", "BabarSquad", "CricNerd_42", "SpinWizard", "PaceMaster",
    "DreamPlayer11", "MatchDay_Vibes", "ShotGuru", "BowlingYorker", "MaidanStar",
    "CricTweeter", "Dhoni_Fan", "ShaheenArmy", "LastOverThrill", "BoundaryKing",
    "SlipCatcher", "PitchReport", "DugoutFan", "ThirdUmpire", "SilkySmooth",
    "RunMachine", "WicketAlert", "NightWatchman", "ReverseSwing", "Googly_Master",
    "CoverDrive_10", "SquareCut", "UpperCut_6", "HelicopterShot", "ScoopKing",
    "LegSpinner", "Chinaman_XI", "OutSwinger", "InSwinger", "FullToss_Fail",
    "NoBall_Noob", "WideAlert", "FreeHitHero", "PowerPlay_Pro", "DeathOver_Boss",
    "RunOut_Panic", "CaughtBehind", "CleanBowled", "LBW_Appeal", "DRS_Review",
    "SuperOver_Fan", "MatchFixAlert", "RainPereira", "DilScoop", "Flamingo_Shot",
    "Doosra_King", "ArmBall_Pro", "TopEdge_Pain", "InsideEdge", "ThickEdge",
    "FineGlance", "LateFlick", "OnDrive_Pure", "OffDrive_Art", "PullShot_King"
]

HYPE_TEMPLATES = [
    "LET'S GOOOOO! 🔥🔥🔥",
    "WHAT A SHOT! {batter} on fire! 🔥",
    "Kya maar raha hai {batter}! 💪",
    "{batter} is in beast mode! 🐅",
    "This is INSANE! What a match! 🏏",
    "SIXXXX! {batter} ne udaa diya! 🚀",
    "BOUNDARY! Clean hit! 💥",
    "Crowd going CRAZY! 🎉",
    "Ab maza aayega! 😍",
    "WHAT A BALL! What a game!",
    "Yeh match toh classic hai! 🏆",
    "{team_batting} fans screaming rn! 🗣",
    "Dream11 pe banayi thi team, sahi laga! 😎",
    "I can't breathe! This game! 😱",
    "YESSSSS! That's what we came for!",
    "Absolutely SMASHED! {batter} OP! 🔥",
    "Goosebumps moment right here! 🙌",
    "THIS IS WHY WE WATCH CRICKET! 🏏❤️",
    "Bhai kya scene hai! 🎬",
    "Ab aaya mood! {team_batting}! 🎊",
]

BANTER_TEMPLATES = [
    "Bhai tere bowling action se acha mera hai gully mein 😂",
    "{bowler} ki bowling dekh ke neend aa rahi hai 😴",
    "My grandma bowls faster than this lol",
    "Fielding dekho fielding 😂 comedy show hai",
    "Meanwhile {bowler} thinking about retirement 💀",
    "Yeh pitch hai ya highway? 🛣",
    "Imagine paying to watch this 😂",
    "Both teams trying to lose 🤣",
    "Commentary bhi bore ho gaye hain",
    "Koi {bowler} ko batao wicket leni hai 😂",
    "This over feels like forever ⏰",
    "Bro thinks he's {batter} 😂",
    "Gully cricket vibes rn 🏏",
    "Umpire bhi confused hai 😅",
    "Pitch doing more than {bowler} 💀",
]

ANALYSIS_TEMPLATES = [
    "RRR climbing now, {team_batting} need to accelerate",
    "Partnership building nicely, {runs} runs so far",
    "This is the key phase - need wickets here",
    "{bowler} bowling well, economy under control",
    "{batter} needs to rotate strike more",
    "Death overs will decide this game",
    "Powerplay going well for {team_batting}",
    "Need at least {runs_needed} from last 5 overs",
    "The chase is ON! Par score around here",
    "Pressure building on {team_batting} now",
    "Dot balls are gold in this phase 💎",
    "{batter} SR is exactly what's needed rn",
    "Middle overs are key in MCG chases",
]

QUESTION_TEMPLATES = [
    "Koi batao {batter} ka SR kya hai?",
    "How many overs left for {bowler}?",
    "Is this pitch getting slower?",
    "Who's the next batter?",
    "Rain forecast kya hai? 🌧",
    "What's the par score here?",
    "DRS remaining kitne hain?",
    "Koi stream link do yaar 😭",
    "Is {batter} injured or just tired?",
    "When did {team_batting} last win from here?",
]

ROAST_TEMPLATES = [
    "{bowler} bowling pies at this point 🥧",
    "Even I could bat better than this 🙄",
    "Bro forgot how to bat 💀",
    "That was village cricket level 😂",
    "Koi coach ko bulao please 📞",
    "Worst over I've seen this year",
    "My fantasy team is crying rn 😢",
    "What was THAT shot? 🤦",
    "Umpire should get player of match tbh",
    "Drop catch? Classic 😂",
]

SHOUTOUT_TEMPLATES = [
    "🎉 SHOUT OUT to all {team_batting} fans watching! Let's go!",
    "Sending love to this watch-along fam! 💛",
    "🔥 SHOUT OUT - {batter} is MY PLAYER! Go king!",
    "Big up to all the night owls watching! 🦉",
    "SHOUT OUT to the chat! Best fans ever! 🏏",
    "💰 SHOUT OUT - This match is everything!",
    "Representing {team_batting}! Let's get this W! 🏆",
    "SHOUT OUT from Mumbai! Jai Hind! 🇮🇳",
]

ABUSE_TEMPLATES = [
    "This umpire is blind I swear",
    "Pathetic batting absolutely pathetic",
    "Worst bowling I've ever seen garbage",
    "Rubbish game so far what is this",
    "Hopeless performance just hopeless",
    "Terrible shot terrible thinking",
    "This is painful to watch honestly",
    "Shameful display of cricket",
    "Get off the field if you can't play",
    "What a joke of a delivery",
]

NEUTRAL_TEMPLATES = [
    "Good game so far 👍",
    "Watching from Delhi, nice match",
    "First time in this watch-along!",
    "GG everyone",
    "Cricket at its finest",
]

TYPE_TEMPLATES = {
    "hype": HYPE_TEMPLATES,
    "banter": BANTER_TEMPLATES,
    "analysis": ANALYSIS_TEMPLATES,
    "question": QUESTION_TEMPLATES,
    "roast": ROAST_TEMPLATES,
    "shoutout": SHOUTOUT_TEMPLATES,
    "abuse": ABUSE_TEMPLATES,
    "neutral": NEUTRAL_TEMPLATES,
}


def generate_chat_fallback(balls, total_messages=None, tensions=None):
    """Generate simulated chat using templates distributed by tension."""
    if total_messages is None:
        total_messages = config.CHAT_TOTAL_MESSAGES

    rng = random.Random(42)
    handles = HANDLES[:config.CHAT_HANDLES_COUNT]
    messages = []

    # Distribute messages by over, with more during high-action phases
    overs_in_match = set()
    for b in balls:
        overs_in_match.add((b["innings"], b["over"]))

    over_list = sorted(overs_in_match)
    total_overs = len(over_list)

    # Base messages per over: at least 2 per over
    msgs_per_over = {k: 2 for k in over_list}

    # Weight overs by tension and boost 3 overs after any high-tension ball
    over_weights = {k: 1.0 for k in over_list}
    
    if tensions is not None and len(tensions) == len(balls):
        # Identify high-tension balls (tension >= 65)
        high_tension_overs = set()
        for i, t in enumerate(tensions):
            if t["tension"] >= 65:
                b = balls[i]
                high_tension_overs.add((b["innings"], b["over"]))
        
        # Boost high-tension overs and the 3 overs following each
        for idx, (inn, ov) in enumerate(over_list):
            if (inn, ov) in high_tension_overs:
                over_weights[(inn, ov)] += 3.0
                # Boost next 3 overs
                for step in range(1, 4):
                    if idx + step < len(over_list):
                        next_ov = over_list[idx + step]
                        over_weights[next_ov] += 2.0
            elif inn == 2 and ov >= 15:
                over_weights[(inn, ov)] += 2.5
    else:
        for inn, ov in over_list:
            if inn == 2 and ov >= 15:
                over_weights[(inn, ov)] = 4.0
            elif inn == 2 and ov >= 10:
                over_weights[(inn, ov)] = 2.5
            elif inn == 2:
                over_weights[(inn, ov)] = 1.5

    # Distribute remaining messages according to weights
    current_total = sum(msgs_per_over.values())
    remaining = total_messages - current_total

    if remaining > 0:
        total_w = sum(over_weights.values())
        for k in over_list:
            extra = int(remaining * over_weights[k] / total_w)
            msgs_per_over[k] += extra

    # Adjust rounding differences to hit exactly total_messages
    current_total = sum(msgs_per_over.values())
    diff = total_messages - current_total
    if diff > 0:
        # Add to the most intense overs (end of chase)
        for k in reversed(over_list):
            msgs_per_over[k] += 1
            diff -= 1
            if diff == 0:
                break
    elif diff < 0:
        for k in over_list:
            if msgs_per_over[k] > 2:
                msgs_per_over[k] -= 1
                diff += 1
                if diff == 0:
                    break

    msg_id = 0
    for inn, ov in over_list:
        count = msgs_per_over[(inn, ov)]
        # Get balls in this over
        over_balls = [b for b in balls if b["innings"] == inn and b["over"] == ov]
        if not over_balls:
            continue

        # Get context for templates
        last_ball = over_balls[-1]
        team_batting = last_ball["team_batting"]
        batter = last_ball["batter"]
        bowler = last_ball["bowler"]
        runs_needed = last_ball.get("runs_needed", 0)

        for _ in range(count):
            # Pick type based on mix
            r = rng.random()
            cumulative = 0
            msg_type = "hype"
            for t, prob in config.CHAT_TYPE_MIX.items():
                cumulative += prob
                if r < cumulative:
                    msg_type = t
                    break

            templates = TYPE_TEMPLATES.get(msg_type, NEUTRAL_TEMPLATES)
            template = rng.choice(templates)

            # Fill template
            text = template.format(
                batter=batter,
                bowler=bowler,
                team_batting=team_batting,
                runs=last_ball["cum_runs"],
                runs_needed=runs_needed,
            )

            # Ensure under 120 chars
            if len(text) > config.CHAT_MAX_TEXT_LEN:
                text = text[:config.CHAT_MAX_TEXT_LEN - 3] + "..."

            # Pick a ball_idx from this over
            ref_ball = rng.choice(over_balls)

            # Language
            lang = "hinglish" if rng.random() < config.CHAT_HINGLISH_RATIO else "en"

            # Team side
            team_sides = ["India", "Pakistan", "neutral"]
            team_side = rng.choice(team_sides)

            # Pinned / shoutout
            is_pinned = msg_type == "shoutout" or (rng.random() < 0.03)
            dreambucks = rng.choice([10, 20, 50, 100, 200, 500]) if (is_pinned or msg_type == "shoutout") else 0

            messages.append({
                "id": msg_id,
                "ball_idx": ref_ball["ball_idx"],
                "display_over": ref_ball["display_over"],
                "handle": rng.choice(handles),
                "text": text,
                "lang": lang,
                "type": msg_type,
                "team_side": team_side,
                "is_pinned": is_pinned,
                "dreambucks": dreambucks,
            })
            msg_id += 1

    return messages[:total_messages]


def generate_vibe_fallback(innings, over_num, messages, balls):
    """Generate vibe data for an over using templates."""
    # Balls in this over
    over_balls = [b for b in balls if b["innings"] == innings and b["over"] == over_num]
    over_ball_indices = set(b["ball_idx"] for b in over_balls)
    
    # Also previous over balls
    prev_balls = [b for b in balls if b["innings"] == innings and b["over"] == over_num - 1]
    window_indices = over_ball_indices.union(set(b["ball_idx"] for b in prev_balls))

    # Messages in this over and window
    over_msgs = [m for m in messages if m["ball_idx"] in over_ball_indices]
    window_msgs = [m for m in messages if m["ball_idx"] in window_indices]
    active_msgs = window_msgs if window_msgs else over_msgs if over_msgs else messages[:5]

    # Count types
    type_counts = {}
    for m in over_msgs:
        type_counts[m["type"]] = type_counts.get(m["type"], 0) + 1

    # Determine mood based on events in this over
    has_wicket = any(b["is_wicket"] for b in over_balls)
    has_six = any(b["runs_batter"] == 6 for b in over_balls)
    has_four = any(b["runs_batter"] == 4 for b in over_balls)
    total_runs = sum(b["runs_total"] for b in over_balls)

    if has_wicket:
        mood = random.randint(72, 92)
        mood_label = random.choice(["Heartbreak", "Electric"])
        themes = ["Wicket drama!", "Game changing moment", "Chat exploding"]
    elif has_six:
        mood = random.randint(75, 96)
        mood_label = "Hyped"
        themes = ["Six hit cleanly", "Crowd goes wild", "Maximum in MCG"]
    elif has_four:
        mood = random.randint(60, 80)
        mood_label = "Hyped"
        themes = ["Boundaries flowing", "Good batting display", "Fans loving it"]
    elif total_runs <= 3:
        mood = random.randint(20, 42)
        mood_label = "Nervous"
        themes = ["Tight bowling spell", "Pressure mounting", "Dot balls piling"]
    else:
        mood = random.randint(45, 65)
        mood_label = "Chilling"
        themes = ["Steady progress made", "Building the chase", "Solid over"]

    # Pick hottest take: prefer shoutout or highest dreambucks, or highest excitement
    hottest_candidates = [m for m in active_msgs if m.get("is_pinned") or m.get("dreambucks", 0) > 0 or m.get("type") in ("hype", "shoutout")]
    hottest = hottest_candidates[0]["id"] if hottest_candidates else active_msgs[0]["id"]

    # Pick funniest take: prefer banter or roast
    funny_candidates = [m for m in active_msgs if m.get("type") in ("banter", "roast")]
    funniest = funny_candidates[0]["id"] if funny_candidates else (active_msgs[-1]["id"] if active_msgs else 0)

    abuse_count = type_counts.get("abuse", 0)
    banter_count = type_counts.get("banter", 0) + type_counts.get("roast", 0)

    batting_name = over_balls[-1]["team_batting"] if over_balls else ("India" if innings == 2 else "Pakistan")
    summary_options = [
        f"Chat buzzing as {batting_name} push on in over {over_num + 1}",
        f"Fans reacting intensely to action in over {over_num + 1}",
        f"Electric energy across the watch-along room right now",
        f"Pressure building rapidly with every single ball bowled",
    ]
    summary_text = random.choice(summary_options)
    # Ensure under 14 words
    summary_words = summary_text.split()
    if len(summary_words) >= 14:
        summary_text = " ".join(summary_words[:13])

    return {
        "over": over_num,
        "innings": innings,
        "themes": [t for t in themes[:3] if len(t.split()) < 8],
        "mood": mood,
        "mood_label": mood_label,
        "hottest_take": hottest,
        "funniest": funniest,
        "banter_tone": "Heated" if banter_count >= 3 else "Playful",
        "abuse_count": abuse_count,
        "summary_line": summary_text,
    }


def generate_walkin_fallback(state, vibe=None, language="english"):
    """Generate Walk-In Ready card using templates."""
    if state is None:
        return {
            "headline": "Match About to Begin!",
            "story": f"India and Pakistan are set to clash at the MCG. The toss is done and we are about to begin.",
            "what_matters_now": "The match is about to start - perfect timing to join!",
            "watch_this_player": {"name": "Virat Kohli", "why": "Always delivers in big matches"},
            "room_mood": "Hyped",
            "join_line": "Get in here, the watch-along is buzzing! 🏏",
        }

    innings = state["innings"]
    score = state["score"]
    wickets = state["wickets"]
    overs = state["overs"]
    team = state["team_batting"]

    if innings == 1:
        headline = f"{team} Building!"
        story = f"{team} are {score}/{wickets} after {overs} overs. "
        if state.get("projected_score"):
            story += f"On track for around {state['projected_score']}."
        else:
            story += "Building their innings steadily."
        what_matters = f"Watch the run rate - {team} looking to accelerate."
    else:
        target = state.get("target", 0)
        runs_needed = state.get("runs_needed", 0)
        balls_left = state.get("balls_left", 0)
        chase_val = state.get("chase_meter", 50)

        headline = f"Chase {'On' if chase_val and chase_val > 40 else 'Tight'}!"
        story = f"{team} are {score}/{wickets} chasing {target}. They need {runs_needed} runs off {balls_left} balls."
        what_matters = f"Required rate is {state.get('rrr', 0)} - {'very gettable' if runs_needed < balls_left else 'pressure is on'}!"

    # Watch this player
    batters = state.get("current_batters", [])
    if batters:
        wp = batters[0]
        watch_player = {"name": wp["name"], "why": f"Batting on {wp['runs']} off {wp['balls']} balls"}
    else:
        watch_player = {"name": "Virat Kohli", "why": "Key player in the chase"}

    room_mood = vibe.get("mood_label", "Hyped") if vibe else "Hyped"

    if language == "hinglish":
        join_line = "Chal andar aa, maza aa raha hai! 🏏🔥"
    else:
        join_line = "Jump in, the watch-along is electric! 🏏🔥"

    return {
        "headline": headline[:40],
        "story": story,
        "what_matters_now": what_matters,
        "watch_this_player": watch_player,
        "room_mood": room_mood,
        "join_line": join_line,
    }


def generate_alert_line_fallback(alert, language="english"):
    """Generate alert why-now line using templates."""
    facts = alert.get("facts", {})
    trigger = alert.get("trigger", "swing")
    severity = alert.get("severity", "Watch")

    if trigger == "wicket":
        player = facts.get("wicket", "batter")
        if language == "hinglish":
            return f"Wicket! {player} out! Match mein twist aa gaya!"
        return f"Wicket! {player} is out. This changes the game!"
    elif trigger == "six":
        batter = facts.get("batter", "batter")
        if language == "hinglish":
            return f"CHHAKKA! {batter} ne stadium ke bahar maara!"
        return f"SIX! {batter} smashes it out of the park!"
    elif trigger == "four":
        batter = facts.get("batter", "batter")
        if language == "hinglish":
            return f"Boundary! {batter} ki kamaal ki shot!"
        return f"FOUR! {batter} finds the gap beautifully!"
    elif trigger == "close_finish":
        rn = facts.get("runs_needed", "?")
        bl = facts.get("balls_left", "?")
        if language == "hinglish":
            return f"Last over drama! {rn} chahiye {bl} balls mein!"
        return f"Thriller alert! {rn} needed off {bl} balls!"
    else:
        score = facts.get("score", "?")
        if language == "hinglish":
            return f"Match garam ho raha hai! Score: {score}"
        return f"Tension rising! Score at {score}!"

