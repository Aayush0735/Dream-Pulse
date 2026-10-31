"""Unit tests for all logic modules."""
import sys
import os
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logic.parse import parse_match_json, verify_totals, get_star_players
from logic.chase import chase_meter, projected_score
from logic.tension import compute_tension, smooth_tension, find_key_moments, get_phase, event_points
from logic.alerts import generate_alerts, determine_trigger, determine_severity
from logic.state import state_at


class TestChaseMeter(unittest.TestCase):
    def test_chase_complete(self):
        """Chase complete when runs_needed <= 0."""
        self.assertEqual(chase_meter(0, 10, 5), 1.0)
        self.assertEqual(chase_meter(-5, 10, 5), 1.0)

    def test_all_out(self):
        """All out gives 0.0."""
        self.assertEqual(chase_meter(50, 30, 0), 0.0)

    def test_no_balls_left(self):
        """No balls left with runs needed gives 0.0."""
        self.assertEqual(chase_meter(10, 0, 5), 0.0)

    def test_easy_chase(self):
        """Easy chase should give high probability."""
        result = chase_meter(10, 60, 10)
        self.assertGreater(result, 0.8)

    def test_tough_chase(self):
        """Tough chase should give low probability."""
        result = chase_meter(50, 12, 3)
        self.assertLess(result, 0.3)

    def test_clamping(self):
        """Values should be clamped between 0.02 and 0.98."""
        result = chase_meter(1, 120, 10)
        self.assertLessEqual(result, 0.98)
        result = chase_meter(100, 6, 1)
        self.assertGreaterEqual(result, 0.02)

    def test_mid_chase(self):
        """Mid-chase should be around 0.5."""
        # Par-ish scenario
        result = chase_meter(54, 36, 7)  # 9 rpo, 7 wickets, ~par
        self.assertGreater(result, 0.2)
        self.assertLess(result, 0.8)


class TestProjectedScore(unittest.TestCase):
    def test_basic(self):
        """Basic projected score."""
        result = projected_score(50, 60, 60)
        self.assertGreater(result, 50)
        self.assertIsInstance(result, int)

    def test_zero_balls(self):
        """With no balls bowled."""
        result = projected_score(0, 120, 0)
        self.assertGreater(result, 100)  # Should project based on avg

    def test_high_rate(self):
        """High run rate should project high."""
        result = projected_score(100, 60, 60)
        self.assertGreater(result, 150)


class TestPhase(unittest.TestCase):
    def test_powerplay(self):
        label, mult = get_phase(0)
        self.assertEqual(label, "Powerplay")
        self.assertEqual(mult, 1.2)
        label, mult = get_phase(5)
        self.assertEqual(label, "Powerplay")

    def test_middle(self):
        label, mult = get_phase(6)
        self.assertEqual(label, "Middle")
        self.assertEqual(mult, 1.0)
        label, mult = get_phase(14)
        self.assertEqual(label, "Middle")

    def test_death(self):
        label, mult = get_phase(15)
        self.assertEqual(label, "Death")
        self.assertEqual(mult, 1.4)
        label, mult = get_phase(19)
        self.assertEqual(label, "Death")


class TestEventPoints(unittest.TestCase):
    def test_wicket(self):
        ball = {"is_wicket": True, "runs_batter": 0, "runs_total": 0, "legal": True}
        self.assertEqual(event_points(ball), 6)

    def test_six(self):
        ball = {"is_wicket": False, "runs_batter": 6, "runs_total": 6, "legal": True}
        self.assertEqual(event_points(ball), 4)

    def test_four(self):
        ball = {"is_wicket": False, "runs_batter": 4, "runs_total": 4, "legal": True}
        self.assertEqual(event_points(ball), 2)

    def test_dot(self):
        ball = {"is_wicket": False, "runs_batter": 0, "runs_total": 0, "legal": True}
        self.assertEqual(event_points(ball), 0.5)

    def test_wide(self):
        ball = {"is_wicket": False, "runs_batter": 0, "runs_total": 1, "legal": False}
        self.assertEqual(event_points(ball), 1)


class TestTension(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, cls.match_data = parse_match_json(config.MATCH_JSON)
        cls.tensions = compute_tension(cls.balls)

    def test_tension_count(self):
        """Tension computed for every ball."""
        self.assertEqual(len(self.tensions), len(self.balls))

    def test_tension_range(self):
        """All tensions between 0 and 100."""
        for t in self.tensions:
            self.assertGreaterEqual(t["tension"], 0)
            self.assertLessEqual(t["tension"], 100)

    def test_smoothing(self):
        """Smoothing produces same-length output."""
        smoothed = smooth_tension(self.tensions)
        self.assertEqual(len(smoothed), len(self.tensions))

    def test_peaks_in_final_overs(self):
        """In a close chase, tension peaks should appear in the final overs."""
        # Get balls in innings 2, death overs
        death_tensions = [
            t["tension"] for i, t in enumerate(self.tensions)
            if self.balls[i]["innings"] == 2 and self.balls[i]["over"] >= 15
        ]
        all_tensions = [t["tension"] for t in self.tensions]
        if death_tensions:
            avg_death = sum(death_tensions) / len(death_tensions)
            avg_all = sum(all_tensions) / len(all_tensions)
            # Death overs should have higher avg tension
            self.assertGreater(avg_death, avg_all * 0.8)


class TestKeyMoments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, _ = parse_match_json(config.MATCH_JSON)
        cls.tensions = compute_tension(cls.balls)
        cls.moments = find_key_moments(cls.tensions, cls.balls)

    def test_count(self):
        """Should find exactly 5 key moments."""
        self.assertEqual(len(self.moments), 5)

    def test_spacing(self):
        """Key moments should be spaced at least 12 balls apart."""
        for i in range(len(self.moments)):
            for j in range(i + 1, len(self.moments)):
                gap = abs(self.moments[i]["ball_idx"] - self.moments[j]["ball_idx"])
                self.assertGreaterEqual(gap, config.MOMENTS_MIN_GAP)

    def test_have_reasons(self):
        """Each moment should have a reason."""
        for m in self.moments:
            self.assertIn("reason", m)
            self.assertTrue(len(m["reason"]) > 0)

    def test_print_moments(self):
        """Print moments for sanity check."""
        print("\nKey Moments:")
        for m in self.moments:
            print(f"  #{m['rank']} Over {m['display_over']} (Inn {m['innings']}): "
                  f"{m['score']} - {m['reason']} (tension: {m['tension']})")


class TestAlerts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, _ = parse_match_json(config.MATCH_JSON)
        cls.tensions = compute_tension(cls.balls)

    def test_alert_generation(self):
        """Should generate alerts."""
        alerts = generate_alerts(self.balls, self.tensions, "Normal")
        self.assertGreater(len(alerts), 0)

    def test_alert_gap(self):
        """Alerts should respect minimum gap."""
        alerts = generate_alerts(self.balls, self.tensions, "Normal")
        for i in range(1, len(alerts)):
            gap = alerts[i]["ball_idx"] - alerts[i - 1]["ball_idx"]
            self.assertGreaterEqual(gap, config.ALERT_GAP_HIGH)

    def test_sensitivity_ordering(self):
        """More sensitive setting should produce more alerts."""
        calm = generate_alerts(self.balls, self.tensions, "Calm")
        normal = generate_alerts(self.balls, self.tensions, "Normal")
        hyped = generate_alerts(self.balls, self.tensions, "Hyped")
        self.assertGreaterEqual(len(hyped), len(normal))
        self.assertGreaterEqual(len(normal), len(calm))

    def test_severity(self):
        """Test severity determination."""
        self.assertEqual(determine_severity(90), "Hot")
        self.assertEqual(determine_severity(70), "Rising")
        self.assertEqual(determine_severity(40), "Watch")


class TestState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, _ = parse_match_json(config.MATCH_JSON)
        cls.tensions = compute_tension(cls.balls)
        cls.moments = find_key_moments(cls.tensions, cls.balls)

    def test_state_at_start(self):
        """State at ball 0."""
        st = state_at(0, self.balls, self.tensions, self.moments)
        self.assertIsNotNone(st)
        self.assertEqual(st["innings"], 1)
        self.assertEqual(st["ball_idx"], 0)

    def test_state_at_end(self):
        """State at last ball."""
        last = len(self.balls) - 1
        st = state_at(last, self.balls, self.tensions, self.moments)
        self.assertIsNotNone(st)

    def test_state_has_required_keys(self):
        """State should have all required keys."""
        st = state_at(100, self.balls, self.tensions, self.moments)
        required = ["ball_idx", "innings", "team_batting", "score", "wickets",
                     "overs", "balls_left", "crr", "current_batters",
                     "current_bowler", "last_12", "partnership", "phase", "what_next"]
        for key in required:
            self.assertIn(key, st, f"Missing key: {key}")

    def test_innings_2_has_chase(self):
        """Innings 2 state should have chase meter."""
        # Find first ball of innings 2
        for b in self.balls:
            if b["innings"] == 2:
                st = state_at(b["ball_idx"], self.balls, self.tensions, self.moments)
                self.assertIsNotNone(st.get("chase_meter"))
                self.assertIsNotNone(st.get("runs_needed"))
                break

    def test_chase_ends_at_1_or_0(self):
        """Chase meter should end at 1.0 (won) or 0.0 (lost)."""
        last_ball = self.balls[-1]
        if last_ball["innings"] == 2:
            st = state_at(last_ball["ball_idx"], self.balls, self.tensions, self.moments)
            chase = st["chase_meter"]
            # India won, so it should be 100
            self.assertEqual(chase, 100.0)


class TestParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balls, cls.match_data = parse_match_json(config.MATCH_JSON)

    def test_totals_match(self):
        """Totals should match the source file."""
        self.assertTrue(verify_totals(self.balls, self.match_data))

    def test_legal_balls_limit(self):
        """Legal balls per innings should be at most 120."""
        for inn in [1, 2]:
            legal = sum(1 for b in self.balls if b["innings"] == inn and b["legal"])
            self.assertLessEqual(legal, 120)

    def test_star_players(self):
        """Star players should be found."""
        stars = get_star_players(self.balls)
        self.assertEqual(len(stars["batters"]), 3)
        self.assertEqual(len(stars["bowlers"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

