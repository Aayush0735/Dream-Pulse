"""Generate vibe data per over."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json
from ai.fallbacks import generate_vibe_fallback
from ai.claude_client import call_claude, get_client
from ai.prompts import VIBE_PROMPT
from ai.validate import validate_vibe


def generate_vibe_with_ai(balls, messages):
    """Generate vibe for each over using Claude."""
    client = get_client()
    vibes = []

    overs_set = sorted(set((b["innings"], b["over"]) for b in balls))

    for inn, ov in overs_set:
        over_msgs = [m for m in messages
                     if any(b["ball_idx"] == m["ball_idx"] and b["innings"] == inn and b["over"] == ov
                            for b in balls)]
        # Also get prev over messages
        prev_msgs = [m for m in messages
                     if any(b["ball_idx"] == m["ball_idx"] and b["innings"] == inn and b["over"] == ov - 1
                            for b in balls)]

        over_balls = [b for b in balls if b["innings"] == inn and b["over"] == ov]

        events = []
        for b in over_balls:
            e = {"runs": b["runs_total"], "batter": b["batter"]}
            if b["is_wicket"]:
                e["wicket"] = b["player_out"]
            if b["runs_batter"] >= 4:
                e["boundary"] = b["runs_batter"]
            events.append(e)

        if client:
            all_msgs = prev_msgs + over_msgs
            prompt = VIBE_PROMPT + f"\n\nMessages:\n{json.dumps([{'text': m['text'], 'type': m['type'], 'id': m['id']} for m in all_msgs[:30]], indent=2)}"
            prompt += f"\n\nEvents:\n{json.dumps(events, indent=2)}"
            prompt += f"\n\nOver: {inn}.{ov}"

            result = call_claude(prompt, temperature=config.TEMP_DEFAULT)
            if result:
                result["over"] = ov
                result["innings"] = inn
                # Compute abuse_count in code, not from model
                result["abuse_count"] = sum(1 for m in over_msgs if m.get("type") == "abuse")
                valid, errors = validate_vibe(result)
                if valid:
                    vibes.append(result)
                    continue

        # Fallback
        vibe = generate_vibe_fallback(inn, ov, messages, balls)
        vibe["abuse_count"] = sum(1 for m in over_msgs if m.get("type") == "abuse")
        vibes.append(vibe)

    return vibes


if __name__ == "__main__":
    balls, _ = parse_match_json(config.MATCH_JSON)
    with open(config.CHAT_JSON, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print("Generating vibes...")
    vibes = generate_vibe_with_ai(balls, messages)

    print(f"Generated {len(vibes)} vibe entries")
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    with open(config.VIBE_JSON, 'w', encoding='utf-8') as f:
        json.dump(vibes, f, indent=2, ensure_ascii=False)
    print(f"Saved to {config.VIBE_JSON}")

