"""Build all precomputed data in order."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def main():
    print("=" * 60)
    print("Building all precomputed data...")
    print("=" * 60)

    # Step 1: Generate chat
    print("\n--- Step 1: Generating chat ---")
    from precompute.gen_chat import generate_chat_with_ai
    from logic.parse import parse_match_json
    from ai.fallbacks import generate_chat_fallback
    import json

    balls, _ = parse_match_json(config.MATCH_JSON)

    from logic.tension import compute_tension
    tensions = compute_tension(balls)

    if config.ANTHROPIC_API_KEY:
        messages = generate_chat_with_ai(balls)
    else:
        messages = generate_chat_fallback(balls, config.CHAT_TOTAL_MESSAGES, tensions)

    with open(config.CHAT_JSON, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Chat: {len(messages)} messages saved")

    # Step 2: Generate vibes
    print("\n--- Step 2: Generating vibes ---")
    from precompute.gen_vibe import generate_vibe_with_ai
    vibes = generate_vibe_with_ai(balls, messages)
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    with open(config.VIBE_JSON, 'w', encoding='utf-8') as f:
        json.dump(vibes, f, indent=2, ensure_ascii=False)
    print(f"Vibes: {len(vibes)} entries saved")

    # Step 3: Generate Walk-In Ready
    print("\n--- Step 3: Generating Walk-In Ready ---")
    from precompute.gen_walkin import generate_walkin_with_ai
    walkins = generate_walkin_with_ai(balls, vibes)
    with open(config.WALKIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(walkins, f, indent=2, ensure_ascii=False)
    print(f"Walk-In: {len(walkins)} entries saved")

    # Step 4: Generate alert lines
    print("\n--- Step 4: Generating alerts ---")
    from precompute.gen_alerts import generate_alert_lines
    from logic.tension import compute_tension
    tensions = compute_tension(balls)
    alerts = generate_alert_lines(balls, tensions)
    with open(config.ALERTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"Alerts: {len(alerts)} entries saved")

    print("\n" + "=" * 60)
    print("All precomputed data built successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

