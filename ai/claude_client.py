"""Claude API client with retry, JSON parsing, and fallback."""
import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_client():
    """Get Anthropic client if API key is available."""
    if not config.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    except Exception:
        return None


def strip_code_fences(text):
    """Remove markdown code fences from response."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()


def call_claude(prompt, system="", temperature=None, max_tokens=4096):
    """
    Call Claude API with retry logic.
    Returns parsed JSON or None.
    """
    client = get_client()
    if client is None:
        return None

    if temperature is None:
        temperature = config.TEMP_DEFAULT

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system if system else "You are a helpful assistant that returns only valid JSON.",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text
            text = strip_code_fences(text)
            return json.loads(text)
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return None
        except Exception as e:
            print(f"Claude API error (attempt {attempt + 1}): {e}")
            if attempt == 0:
                continue
            return None

    return None

