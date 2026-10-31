"""Generate Walk-In Ready cards at every over boundary, for both languages."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json
from logic.tension import compute_tension, find_key_moments
from logic.state import state_at
from ai.fallbacks import generate_walkin_fallback
from ai.claude_client import call_claude, get_client
from ai.prompts import WALKIN_PROMPT
from ai.validate import validate_walkin


def generate_walkin_with_ai(balls, vibes):
    """Generate Walk-In Ready for every over boundary, both languages."""
    client = get_client()
    tensions = compute_tension(balls)
    moments = find_key_moments(tensions, balls)

    walkins = []
    overs_set = sorted(set((b["innings"], b["over"]) for b in balls))

    for inn, ov in overs_set:
        # Find last ball of this over
        over_balls = [b for b in balls if b["innings"] == inn and b["over"] == ov]
        if not over_balls:
            continue
        last_ball_idx = over_balls[-1]["ball_idx"]

        # Get state
        st = state_at(last_ball_idx, balls, tensions, moments)
        if st is None:
            continue

        # Get vibe for this over
        vibe = None
        for v in vibes:
            if v.get("over") == ov and v.get("innings", 1) == inn:
                vibe = v
                break

        for language in ["english", "hinglish"]:
            if client:
                facts = {
                    "innings": st["innings"],
                    "team_batting": st["team_batting"],
                    "score": f"{st['score']}/{st['wickets']}",
                    "overs": st["overs"],
                    "target": st.get("target"),
                    "runs_needed": st.get("runs_needed"),
                    "balls_left": st["balls_left"],
                    "crr": st["crr"],
                    "rrr": st.get("rrr"),
                    "chase_meter": st.get("chase_meter"),
                    "current_batters": st["current_batters"],
                    "key_moments": st["key_moments"],
                    "phase": st["phase"],
                    "what_next": st["what_next"],
                }
                if vibe:
                    facts["room_vibe"] = {
                        "mood_label": vibe.get("mood_label"),
                        "themes": vibe.get("themes"),
                    }

                prompt = WALKIN_PROMPT.format(language=language)
                prompt += f"\n\nFacts:\n{json.dumps(facts, indent=2)}"

                result = call_claude(prompt, temperature=config.TEMP_DEFAULT)
                if result:
                    valid, errors = validate_walkin(result, facts)
                    if not valid:
                        # Retry once
                        prompt += "\n\nIMPORTANT: Use ONLY numbers from the facts above. Previous attempt had errors: " + "; ".join(errors)
                        result = call_claude(prompt, temperature=config.TEMP_DEFAULT)
                        if result:
                            valid, errors = validate_walkin(result, facts)

                    if valid:
                        result["innings"] = inn
                        result["over"] = ov
                        result["language"] = language
                        result["ball_idx"] = last_ball_idx
                        walkins.append(result)
                        continue

            # Fallback
            walkin = generate_walkin_fallback(st, vibe, language)
            walkin["innings"] = inn
            walkin["over"] = ov
            walkin["language"] = language
            walkin["ball_idx"] = last_ball_idx
            walkins.append(walkin)

    return walkins


if __name__ == "__main__":
    balls, _ = parse_match_json(config.MATCH_JSON)
    with open(config.VIBE_JSON, 'r', encoding='utf-8') as f:
        vibes = json.load(f)

    print("Generating Walk-In Ready cards...")
    walkins = generate_walkin_with_ai(balls, vibes)

    print(f"Generated {len(walkins)} Walk-In entries")
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    with open(config.WALKIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(walkins, f, indent=2, ensure_ascii=False)
    print(f"Saved to {config.WALKIN_JSON}")

