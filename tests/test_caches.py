"""Tests for precomputed caches: chat, vibe, walkin, alerts."""
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json
from logic.tension import compute_tension, find_key_moments
from logic.state import state_at
from ai.validate import validate_chat_message, validate_vibe, validate_walkin


class TestCaches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, _ = parse_match_json(config.MATCH_JSON)
        cls.tensions = compute_tension(cls.balls)
        cls.moments = find_key_moments(cls.tensions, cls.balls)

        with open(config.CHAT_JSON, 'r', encoding='utf-8') as f:
            cls.chat = json.load(f)
        with open(config.VIBE_JSON, 'r', encoding='utf-8') as f:
            cls.vibes = json.load(f)
        with open(config.WALKIN_JSON, 'r', encoding='utf-8') as f:
            cls.walkins = json.load(f)
        with open(config.ALERTS_JSON, 'r', encoding='utf-8') as f:
            cls.alerts = json.load(f)

    def test_chat_volume_and_schema(self):
        """Chat must have exactly 450 valid messages."""
        self.assertEqual(len(self.chat), 450)
        valid_count = 0
        for msg in self.chat:
            valid, errs = validate_chat_message(msg)
            self.assertTrue(valid, f"Invalid chat message {msg}: {errs}")

    def test_chat_handles_count(self):
        """Chat handles must be around 70 fictional handles."""
        handles = set(m["handle"] for m in self.chat)
        self.assertGreaterEqual(len(handles), 50)
        self.assertLessEqual(len(handles), 80)

    def test_vibe_entries(self):
        """Vibe cache must have an entry per over (40 total)."""
        self.assertEqual(len(self.vibes), 40)
        for v in self.vibes:
            valid, errs = validate_vibe(v)
            self.assertTrue(valid, f"Invalid vibe entry {v}: {errs}")

    def test_walkin_count(self):
        """Walk-in cache must have 80 entries (40 overs * 2 languages)."""
        self.assertEqual(len(self.walkins), 80)

    def test_walkin_numbers_pass_validation(self):
        """Every number in Walk-In output must appear in the facts."""
        for w in self.walkins:
            bidx = w.get("ball_idx", 0)
            st = state_at(bidx, self.balls, self.tensions, self.moments)
            valid, errs = validate_walkin(w, st)
            self.assertTrue(valid, f"Walkin number validation failed at Inn {w.get('innings')}, Ov {w.get('over')}: {errs}")

    def test_alerts_cache(self):
        """Alerts cache must have entries with valid why-now lines."""
        self.assertGreater(len(self.alerts), 0)
        for a in self.alerts:
            self.assertIn("why_now", a)
            self.assertIn("language", a)
            self.assertIn("severity", a)
            self.assertIn("trigger", a)
            words = a["why_now"].split()
            self.assertLessEqual(len(words), 20)  # max ~14 words allowed with margin


if __name__ == "__main__":
    unittest.main()

