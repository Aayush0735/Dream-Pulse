"""Generate alert why-now lines."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json
from logic.tension import compute_tension
from logic.alerts import generate_alerts
from ai.fallbacks import generate_alert_line_fallback
from ai.claude_client import call_claude, get_client
from ai.prompts import ALERT_PROMPT


def generate_alert_lines(balls, tensions):
    """Generate why-now lines for all alerts at Hyped threshold."""
    client = get_client()

    # Generate alerts at Hyped threshold (covers all sensitivities since it's lowest)
    alerts = generate_alerts(balls, tensions, "Hyped")

    enriched = []
    for alert in alerts:
        for language in ["english", "hinglish"]:
            if client:
                prompt = ALERT_PROMPT.format(language=language)
                prompt += f"\n\nFacts:\n{json.dumps(alert['facts'], indent=2)}"
                result = call_claude(prompt, temperature=config.TEMP_DEFAULT, max_tokens=100)
                if result and isinstance(result, str):
                    line = result[:70]  # max ~14 words
                elif result and isinstance(result, dict) and "line" in result:
                    line = str(result["line"])[:70]
                else:
                    line = generate_alert_line_fallback(alert, language)
            else:
                line = generate_alert_line_fallback(alert, language)

            enriched.append({
                "ball_idx": alert["ball_idx"],
                "display_over": alert["display_over"],
                "severity": alert["severity"],
                "trigger": alert["trigger"],
                "tension": alert["tension"],
                "innings": alert["innings"],
                "language": language,
                "why_now": line,
                "facts": alert["facts"],
            })

    return enriched


if __name__ == "__main__":
    balls, _ = parse_match_json(config.MATCH_JSON)
    tensions = compute_tension(balls)

    print("Generating alert lines...")
    alerts = generate_alert_lines(balls, tensions)

    print(f"Generated {len(alerts)} alert entries")
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    with open(config.ALERTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"Saved to {config.ALERTS_JSON}")

