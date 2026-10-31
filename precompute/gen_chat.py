"""Generate simulated chat data."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json
from ai.fallbacks import generate_chat_fallback
from ai.claude_client import call_claude, get_client
from ai.prompts import CHAT_PROMPT
from ai.validate import validate_chat_message


def generate_chat_with_ai(balls, total_messages=None):
    """Generate chat using Claude API, processing 5 overs at a time."""
    if total_messages is None:
        total_messages = config.CHAT_TOTAL_MESSAGES

    client = get_client()
    if client is None:
        print("No API key, using template fallback for chat generation")
        return generate_chat_fallback(balls, total_messages)

    all_messages = []
    msg_id = 0

    # Group balls by innings and 5-over windows
    overs_set = set()
    for b in balls:
        overs_set.add((b["innings"], b["over"]))
    overs_list = sorted(overs_set)

    # Process in windows of 5 overs
    window_size = 5
    for i in range(0, len(overs_list), window_size):
        window_overs = overs_list[i:i + window_size]
        start_inn, start_ov = window_overs[0]
        end_inn, end_ov = window_overs[-1]

        # Get balls in this window
        window_balls = [
            b for b in balls
            if (b["innings"], b["over"]) in set(window_overs)
        ]

        # Build events summary
        events = []
        for b in window_balls:
            event = {
                "over": b["display_over"],
                "innings": b["innings"],
                "batter": b["batter"],
                "bowler": b["bowler"],
                "runs": b["runs_total"],
                "team": b["team_batting"],
                "score": f"{b['cum_runs']}/{b['cum_wkts']}",
            }
            if b["is_wicket"]:
                event["wicket"] = b["player_out"]
            if b["runs_batter"] >= 4:
                event["boundary"] = b["runs_batter"]
            events.append(event)

        # Estimate messages for this window
        msgs_needed = int(total_messages * len(window_overs) / len(overs_list))
        msgs_needed = max(2 * len(window_overs), msgs_needed)

        prompt = CHAT_PROMPT.format(
            start_over=f"{start_inn}.{start_ov}",
            end_over=f"{end_inn}.{end_ov}"
        )
        prompt += f"\n\nMatch facts:\n{json.dumps(events[:50], indent=2)}"
        prompt += f"\n\nGenerate exactly {msgs_needed} messages."

        result = call_claude(prompt, temperature=config.TEMP_CHAT)

        if result and isinstance(result, list):
            for msg in result:
                # Map to full schema
                ball_candidates = [
                    b for b in window_balls
                    if str(b["over"]) == str(msg.get("over", ""))
                ]
                ref_ball = ball_candidates[0] if ball_candidates else window_balls[0]

                full_msg = {
                    "id": msg_id,
                    "ball_idx": ref_ball["ball_idx"],
                    "display_over": ref_ball["display_over"],
                    "handle": msg.get("handle", f"Fan_{msg_id}"),
                    "text": str(msg.get("text", ""))[:120],
                    "lang": msg.get("lang", "en"),
                    "type": msg.get("type", "hype"),
                    "team_side": msg.get("team_side", "neutral"),
                    "is_pinned": msg.get("type") == "shoutout",
                    "dreambucks": 50 if msg.get("type") == "shoutout" else 0,
                }

                valid, errors = validate_chat_message(full_msg)
                if valid:
                    all_messages.append(full_msg)
                    msg_id += 1

        if len(all_messages) >= total_messages:
            break

    # If we don't have enough, fill with fallback
    if len(all_messages) < total_messages:
        fallback = generate_chat_fallback(balls, total_messages - len(all_messages))
        for msg in fallback:
            msg["id"] = msg_id
            all_messages.append(msg)
            msg_id += 1
            if len(all_messages) >= total_messages:
                break

    return all_messages[:total_messages]


if __name__ == "__main__":
    balls, _ = parse_match_json(config.MATCH_JSON)

    if config.ANTHROPIC_API_KEY:
        print("Generating chat with Claude API...")
        messages = generate_chat_with_ai(balls)
    else:
        print("No API key - generating chat with templates...")
        messages = generate_chat_fallback(balls)

    # Validate
    valid_count = 0
    type_counts = {}
    for msg in messages:
        v, e = validate_chat_message(msg)
        if v:
            valid_count += 1
        t = msg.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\nGenerated {len(messages)} messages ({valid_count} valid)")
    print(f"Type distribution: {type_counts}")
    print(f"Unique handles: {len(set(m['handle'] for m in messages))}")

    # Save
    with open(config.CHAT_JSON, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Saved to {config.CHAT_JSON}")

