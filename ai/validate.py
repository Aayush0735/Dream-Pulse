"""Validation for AI-generated content."""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_numbers(text):
    """Extract all numbers from a text string."""
    if isinstance(text, dict):
        text = str(text)
    return set(re.findall(r'\b\d+\.?\d*\b', str(text)))


def validate_walkin(walkin_data, facts):
    """
    Validate Walk-In Ready output: every number in the output must appear in the facts.
    Returns (is_valid, errors).
    """
    facts_str = str(facts)
    facts_numbers = extract_numbers(facts_str)

    output_str = ""
    for key in ["headline", "story", "what_matters_now", "join_line"]:
        output_str += " " + str(walkin_data.get(key, ""))
    if "watch_this_player" in walkin_data:
        output_str += " " + str(walkin_data["watch_this_player"].get("why", ""))

    output_numbers = extract_numbers(output_str)
    errors = []

    for num in output_numbers:
        if num not in facts_numbers:
            # Allow small numbers that might be ordinals or generic
            try:
                n = float(num)
                if n <= 4 or n == 20:  # Common generic numbers
                    continue
            except ValueError:
                pass
            errors.append(f"Number '{num}' in output not found in facts")

    return len(errors) == 0, errors


def validate_chat_message(msg):
    """Validate a single chat message against schema."""
    required = ["id", "ball_idx", "display_over", "handle", "text", "lang", "type", "team_side", "is_pinned", "dreambucks"]
    errors = []
    for key in required:
        if key not in msg:
            errors.append(f"Missing key: {key}")

    if "text" in msg and len(str(msg["text"])) > 120:
        errors.append(f"Text too long: {len(msg['text'])} chars")

    valid_types = set(["hype", "banter", "analysis", "question", "roast", "shoutout", "abuse", "neutral"])
    if "type" in msg and msg["type"] not in valid_types:
        errors.append(f"Invalid type: {msg['type']}")

    return len(errors) == 0, errors


def validate_vibe(vibe_data):
    """Validate vibe JSON structure."""
    required = ["over", "themes", "mood", "mood_label", "hottest_take", "funniest", "banter_tone", "summary_line"]
    errors = []
    for key in required:
        if key not in vibe_data:
            errors.append(f"Missing key: {key}")

    if "themes" in vibe_data and len(vibe_data["themes"]) > 3:
        errors.append(f"Too many themes: {len(vibe_data['themes'])}")

    if "mood" in vibe_data:
        mood = vibe_data["mood"]
        if not (0 <= mood <= 100):
            errors.append(f"Mood out of range: {mood}")

    valid_labels = {"Nervous", "Hyped", "Heartbreak", "Chilling", "Roasting", "Electric"}
    if "mood_label" in vibe_data and vibe_data["mood_label"] not in valid_labels:
        errors.append(f"Invalid mood_label: {vibe_data['mood_label']}")

    return len(errors) == 0, errors

