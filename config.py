"""Central configuration for Watch-Along Copilot."""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Model ──────────────────────────────────────────────────────
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LIVE_AI = os.getenv("LIVE_AI", "0") == "1"

# ── Paths ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
MATCH_JSON = os.path.join(DATA_DIR, "match.json")
BALLS_CSV = os.path.join(DATA_DIR, "balls.csv")
CHAT_JSON = os.path.join(DATA_DIR, "chat.json")
VIBE_JSON = os.path.join(CACHE_DIR, "vibe.json")
WALKIN_JSON = os.path.join(CACHE_DIR, "walkin.json")
ALERTS_JSON = os.path.join(CACHE_DIR, "alerts.json")

# ── Chase meter constants ──────────────────────────────────────
CHASE_SLOPE = 0.45
CHASE_PAR_BASE = 9.0
CHASE_PAR_WKT_WEIGHT = 0.55
CHASE_PAR_CONST = 0.45
CHASE_PAR_EXP = 0.6
CHASE_MIN = 0.02
CHASE_MAX = 0.98

# ── Projected score (1st innings) ──────────────────────────────
PROJ_CRR_WEIGHT = 0.6
PROJ_AVG_RPB = 8.5 / 6  # ~1.417

# ── Tension constants ─────────────────────────────────────────
TENSION_SWING_WEIGHT = 0.9
EVENT_PTS = {
    "wicket": 6,
    "six": 4,
    "four": 2,
    "dot": 0.5,
    "wide_noball": 1,
    "other": 1,
}
PHASE_MULT = {
    "powerplay": 1.2,   # overs 0-5
    "middle": 1.0,      # overs 6-14
    "death": 1.4,       # overs 15-19
}
CLOSENESS_WEIGHT = 8.0
TENSION_P95_DENOM = 100
STAR_BONUS = 3
TENSION_SMOOTH_WINDOW = 3

# ── Alert thresholds ──────────────────────────────────────────
SENSITIVITY = {
    "Calm": 75,
    "Normal": 60,
    "Hyped": 45,
}
ALERT_GAP_NORMAL = 6
ALERT_GAP_HIGH = 2
ALERT_HIGH_TENSION = 90
ALERT_SEVERITY = {
    "Hot": 80,
    "Rising": 60,
    "Watch": 0,
}

# ── Key moments ───────────────────────────────────────────────
TOP_MOMENTS_COUNT = 5
MOMENTS_MIN_GAP = 12

# ── Chat ──────────────────────────────────────────────────────
CHAT_TOTAL_MESSAGES = 450
CHAT_HANDLES_COUNT = 70
CHAT_MAX_TEXT_LEN = 120
CHAT_TYPE_MIX = {
    "hype": 0.30,
    "banter": 0.20,
    "analysis": 0.15,
    "question": 0.10,
    "roast": 0.10,
    "shoutout": 0.08,
    "abuse": 0.05,
    "neutral": 0.02,
}
CHAT_HINGLISH_RATIO = 0.60

# ── AI temperatures ───────────────────────────────────────────
TEMP_CHAT = 0.7
TEMP_DEFAULT = 0.3

# ── UI colours ────────────────────────────────────────────────
CLR_BG = "#0F0F12"
CLR_CARD = "#1A1A1F"
CLR_CARD_BORDER = "#2A2A31"
CLR_RED = "#D91E2B"
CLR_HOT = "#FF4D4D"
CLR_TEXT = "#FFFFFF"
CLR_MUTED = "#9A9AA6"
CLR_SUCCESS = "#22C55E"
CLR_GOLD = "#F5B301"
CLR_AMBER = "#F59E0B"
CLR_BLUE = "#3B82F6"

# ── UI layout ─────────────────────────────────────────────────
MAX_WIDTH_PX = 430
CARD_RADIUS = 16
PLAY_SPEED = {
    "1x": 1.0,
    "2x": 0.5,
    "5x": 0.2,
}

# ── Match info ────────────────────────────────────────────────
TEAM_A = "India"
TEAM_B = "Pakistan"
MATCH_TITLE = "IND vs PAK • T20 World Cup 2022"
MATCH_VENUE = "MCG, Melbourne"
MATCH_DATE = "2022-10-23"

