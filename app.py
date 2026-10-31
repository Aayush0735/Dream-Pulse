"""
Watch-Along Copilot - Dream11 FDE Assignment
Main Streamlit application.
Independent prototype inspired by public information about Dream11 Watch Along.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os
import math
import time

# ── Config ─────────────────────────────────────────────────────
import config
from logic.parse import parse_match_json, get_star_players
from logic.chase import chase_meter, projected_score
from logic.tension import compute_tension, smooth_tension, find_key_moments
from logic.alerts import generate_alerts
from logic.state import state_at

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Dream11 Watch-Along Copilot",
    page_icon="🏏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Theme Session State ────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "language" not in st.session_state:
    st.session_state.language = "english"
if "ball_idx" not in st.session_state:
    st.session_state.ball_idx = 0
if "playing" not in st.session_state:
    st.session_state.playing = False
if "speed" not in st.session_state:
    st.session_state.speed = "1x"
if "fav_team" not in st.session_state:
    st.session_state.fav_team = "India"
if "fav_player" not in st.session_state:
    st.session_state.fav_player = "V Kohli"
if "sensitivity" not in st.session_state:
    st.session_state.sensitivity = "Normal"
if "show_walkin_card" not in st.session_state:
    st.session_state.show_walkin_card = False

is_dark = (st.session_state.theme == "dark")

# ── CSS Variables & Styling ────────────────────────────────────
dark_css = """
:root {
    --bg-app: #0B0B0E;
    --app-gradient: radial-gradient(circle at 50% -10%, #450A10 0%, #1A0914 30%, #0D0D12 75%, #08080B 100%);
    --card-bg: rgba(22, 22, 28, 0.78);
    --card-bg-solid: #17171F;
    --card-border: rgba(255, 255, 255, 0.08);
    --card-border-top: rgba(255, 255, 255, 0.16);
    --card-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6), 0 0 1px 1px rgba(255, 255, 255, 0.05) inset;
    --text-main: #FFFFFF;
    --text-muted: #94A3B8;
    --text-sub: #64748B;
    --accent-red: #E11D48;
    --accent-red-glow: rgba(225, 29, 72, 0.35);
    --accent-gold: #F5B301;
    --accent-green: #10B981;
    --chase-track: #23232C;
    --chat-bg: rgba(16, 16, 22, 0.7);
    --chat-border: rgba(255, 255, 255, 0.06);
    --pill-bg: #22222B;
    --dialog-bg: #13131A;
}
"""

light_css = """
:root {
    --bg-app: #F8FAFC;
    --app-gradient: radial-gradient(circle at 50% -10%, #FFE4E6 0%, #FFF1F2 25%, #F8FAFC 65%, #F1F5F9 100%);
    --card-bg: rgba(255, 255, 255, 0.88);
    --card-bg-solid: #FFFFFF;
    --card-border: rgba(226, 232, 240, 0.95);
    --card-border-top: rgba(255, 255, 255, 1.0);
    --card-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.06), 0 1px 2px 0 rgba(15, 23, 42, 0.04);
    --text-main: #0F172A;
    --text-muted: #475569;
    --text-sub: #94A3B8;
    --accent-red: #D91E2B;
    --accent-red-glow: rgba(217, 30, 43, 0.2);
    --accent-gold: #D97706;
    --accent-green: #059669;
    --chase-track: #E2E8F0;
    --chat-bg: #F1F5F9;
    --chat-border: #E2E8F0;
    --pill-bg: #E2E8F0;
    --dialog-bg: #FFFFFF;
}
"""

theme_specific_vars = dark_css if is_dark else light_css

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

{theme_specific_vars}

/* Reset Streamlit default headers/footers */
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
header {{visibility: hidden !important;}}
.stDeployButton {{display: none !important;}}

/* Global resets & typography */
* {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}}

.stApp {{
    background: var(--app-gradient) !important;
    background-color: var(--bg-app) !important;
    color: var(--text-main) !important;
    min-height: 100vh;
}}

/* Phone Chassis Constraint (Max 430px, responsive down to 390px) */
.main .block-container {{
    max-width: 430px !important;
    padding: 0.4rem 0.75rem 2rem 0.75rem !important;
    margin: 0 auto !important;
}}

@media (max-width: 430px) {{
    .main .block-container {{
        padding: 0.25rem 0.5rem 1.5rem 0.5rem !important;
    }}
}}

/* Dream11 Glassmorphism Cards */
.d11-card {{
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--card-border);
    border-top: 1px solid var(--card-border-top);
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 11px;
    box-shadow: var(--card-shadow);
    transition: transform 0.2s ease, border-color 0.2s ease;
}}

.d11-card-gold {{
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1.5px solid var(--accent-gold);
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 8px;
    box-shadow: 0 4px 20px -2px rgba(245, 179, 1, 0.15);
}}

/* Header Navigation Bar */
.top-nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0 8px 0;
}}

.brand-badge {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.d11-logo-text {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 6px;
}}

.watchalong-tag {{
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #E11D48, #BE123C);
    color: #FFFFFF;
    padding: 2px 7px;
    border-radius: 6px;
    box-shadow: 0 2px 6px var(--accent-red-glow);
}}

.live-pulse-pill {{
    background: #D91E2B;
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.6px;
    padding: 3px 9px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    box-shadow: 0 0 12px rgba(217, 30, 43, 0.45);
    animation: livePulse 2s infinite ease-in-out;
}}

@keyframes livePulse {{
    0%, 100% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(0.97); opacity: 0.82; }}
}}

/* Scoreboard Elements */
.score-hero {{
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.8px;
    color: var(--text-main);
    font-variant-numeric: tabular-nums;
    line-height: 1.05;
}}

.score-sub {{
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
}}

.target-glow {{
    font-size: 13px;
    font-weight: 800;
    color: var(--accent-gold);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}

/* Ball Delivery Chips */
.ball-chip {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 25px;
    height: 25px;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    margin-right: 3px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}}
.ball-0 {{ background: {"#262630" if is_dark else "#E2E8F0"}; color: var(--text-muted); }}
.ball-1, .ball-2, .ball-3 {{ background: {"#1E1E26" if is_dark else "#F1F5F9"}; color: var(--text-main); border: 1px solid var(--card-border); }}
.ball-4 {{ background: #1D4ED8; color: #FFFFFF; border: 1px solid #3B82F6; }}
.ball-6 {{ background: #B45309; color: #FEF3C7; border: 1px solid #F59E0B; }}
.ball-W {{ background: #BE123C; color: #FFFFFF; border: 1px solid #E11D48; }}
.ball-dot {{ background: {"#181820" if is_dark else "#E2E8F0"}; color: var(--text-sub); }}

/* Sleek Glowing Chase Meter */
.chase-bar-bg {{
    width: 100%;
    height: 9px;
    background: var(--chase-track);
    border-radius: 6px;
    overflow: hidden;
    margin: 6px 0 4px 0;
    position: relative;
}}
.chase-bar-fill {{
    height: 100%;
    border-radius: 6px;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* Alert Notification Cards */
.alert-box {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 10px 12px;
    margin-bottom: 8px;
    box-shadow: var(--card-shadow);
}}

/* Pills */
.pill-chip {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}
.pill-red {{ background: rgba(225, 29, 72, 0.15); color: #FB7185; border: 1px solid rgba(225, 29, 72, 0.3); }}
.pill-amber {{ background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }}
.pill-green {{ background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }}
.pill-blue {{ background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); }}
.pill-muted {{ background: var(--pill-bg); color: var(--text-muted); }}

/* Chat Message Card */
.chat-bubble {{
    padding: 7px 11px;
    margin: 4px 0;
    border-radius: 12px;
    background: var(--chat-bg);
    font-size: 12px;
    border: 1px solid var(--chat-border);
}}

.chat-bubble-pinned {{
    padding: 7px 11px;
    margin: 4px 0;
    border-radius: 12px;
    background: var(--chat-bg);
    font-size: 12px;
    border: 1.5px solid var(--accent-gold);
    box-shadow: 0 2px 10px rgba(245, 179, 1, 0.12);
}}

/* Banter Guard */
details.abuse-guard {{
    background: var(--chat-bg);
    border: 1px dashed var(--text-sub);
    border-radius: 10px;
    padding: 6px 10px;
    margin: 4px 0;
}}
details.abuse-guard summary {{
    cursor: pointer;
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 600;
    user-select: none;
    outline: none;
}}

/* Streamlit Button Tweaks */
div.stButton > button {{
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border: 1px solid var(--card-border) !important;
    background: var(--card-bg-solid) !important;
    color: var(--text-main) !important;
    transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
    border-color: var(--accent-red) !important;
    box-shadow: 0 2px 12px var(--accent-red-glow) !important;
}}

.d11-primary-btn div.stButton > button {{
    background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 16px var(--accent-red-glow) !important;
}}

.d11-primary-btn div.stButton > button:hover {{
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
}}

/* Footer */
.d11-footer {{
    font-size: 10px;
    color: var(--text-sub);
    text-align: center;
    padding: 14px 0 4px 0;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)


# ── SVG Logo Helpers ───────────────────────────────────────────
def get_d11_shield_svg(size=24):
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="9" fill="url(#d11Grad)"/>
        <path d="M9 7.5H16.2C20.5 7.5 24 11 24 15.3C24 19.6 20.5 23.1 16.2 23.1H9V7.5Z" fill="white"/>
        <path d="M12.4 11H15.8C18.2 11 20.2 13 20.2 15.4C20.2 17.8 18.2 19.8 15.8 19.8H12.4V11Z" fill="#D91E2B"/>
        <defs>
            <linearGradient id="d11Grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stop-color="#E11D48"/>
                <stop offset="1" stop-color="#9F1239"/>
            </linearGradient>
        </defs>
    </svg>
    """

def get_team_crest_svg(team_name, size=18):
    if team_name == "India":
        return f"""
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="11" fill="#0284C7" stroke="#38BDF8" stroke-width="1.5"/>
            <path d="M2.5 8.5C4.5 4.5 19.5 4.5 21.5 8.5H2.5Z" fill="#F97316"/>
            <path d="M2.5 15.5C4.5 19.5 19.5 19.5 21.5 15.5H2.5Z" fill="#16A34A"/>
            <circle cx="12" cy="12" r="2.8" fill="#FFFFFF"/>
            <circle cx="12" cy="12" r="1.2" fill="#0369A1"/>
        </svg>
        """
    else:
        return f"""
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="11" fill="#065F46" stroke="#10B981" stroke-width="1.5"/>
            <path d="M13.5 6.5C9.6 7.5 7.5 11.2 8.5 15C9.5 18.5 13.5 20 16.5 18.5C14 18 11.5 15.5 11.5 12.5C11.5 9.5 13.5 7.5 13.5 6.5Z" fill="#FFFFFF"/>
            <polygon points="16.5,8.5 17.5,10.5 19.5,10.5 18,12 18.5,14 16.5,12.8 14.5,14 15,12 13.5,10.5 15.5,10.5" fill="#FFFFFF"/>
        </svg>
        """


# ── Load cached data ──────────────────────────────────────────
@st.cache_data
def load_data():
    balls, match_data = parse_match_json(config.MATCH_JSON)
    stars = get_star_players(balls)
    with open(config.CHAT_JSON, 'r', encoding='utf-8') as f:
        chat = json.load(f)
    with open(config.VIBE_JSON, 'r', encoding='utf-8') as f:
        vibes = json.load(f)
    with open(config.WALKIN_JSON, 'r', encoding='utf-8') as f:
        walkins = json.load(f)
    with open(config.ALERTS_JSON, 'r', encoding='utf-8') as f:
        alerts_cache = json.load(f)
    return balls, match_data, stars, chat, vibes, walkins, alerts_cache

balls, match_data, stars, chat_data, vibes_data, walkins_data, alerts_cache = load_data()
all_star_names = [p["name"] for p in stars["batters"]] + [p["name"] for p in stars["bowlers"]]

# Compute tension with user selected favourite player
@st.cache_data
def get_tensions(fav_player):
    return compute_tension(balls, fav_player)

tensions = get_tensions(st.session_state.fav_player)
smoothed = smooth_tension(tensions)
moments = find_key_moments(tensions, balls)

@st.cache_data
def get_alerts_for_sensitivity(sensitivity, fav_player):
    t = compute_tension(balls, fav_player)
    return generate_alerts(balls, t, sensitivity)

current_alerts = get_alerts_for_sensitivity(st.session_state.sensitivity, st.session_state.fav_player)


# ── Helpers ────────────────────────────────────────────────────
def get_ball_chip_html(val):
    if val == "W":
        return '<span class="ball-chip ball-W">W</span>'
    elif val == "4":
        return '<span class="ball-chip ball-4">4</span>'
    elif val == "6":
        return '<span class="ball-chip ball-6">6</span>'
    elif val == "0":
        return '<span class="ball-chip ball-0">0</span>'
    elif val in ("1", "2", "3"):
        return f'<span class="ball-chip ball-{val}">{val}</span>'
    else:
        return f'<span class="ball-chip ball-dot">{val}</span>'

def get_chase_gradient(pct):
    if pct >= 55:
        return "linear-gradient(90deg, #10B981, #059669)"
    elif pct >= 40:
        return "linear-gradient(90deg, #F59E0B, #D97706)"
    else:
        return "linear-gradient(90deg, #E11D48, #BE123C)"

def get_walkin_for_over(innings, over, language):
    for w in walkins_data:
        if w.get("innings") == innings and w.get("over") == over and w.get("language") == language:
            return w, over
    closest, min_dist = None, float('inf')
    for w in walkins_data:
        if w.get("innings") == innings and w.get("language") == language:
            dist = abs(w.get("over", 0) - over)
            if dist < min_dist:
                min_dist, closest = dist, w
    return closest, (closest.get("over", over) if closest else over)

def get_vibe_for_over(innings, over):
    for v in vibes_data:
        if v.get("innings", 1) == innings and v.get("over") == over:
            return v, over
    closest, min_dist = None, float('inf')
    for v in vibes_data:
        if v.get("innings", 1) == innings:
            dist = abs(v.get("over", 0) - over)
            if dist < min_dist:
                min_dist, closest = dist, v
    return closest, (closest.get("over", over) if closest else over)

def get_alert_line(ball_idx, language):
    for a in alerts_cache:
        if a["ball_idx"] == ball_idx and a.get("language", "english") == language:
            return a.get("why_now", "")
    for a in alerts_cache:
        if a["ball_idx"] == ball_idx:
            return a.get("why_now", "")
    return ""


# ── Walk-In Modal Dialog ───────────────────────────────────────
@st.dialog("🚶 Walk-In Ready • 20s Catch-Up")
def show_walkin_modal(walkin, snap_over):
    if not walkin:
        st.info("No catch-up available. Advance the match clock.")
        return

    headline = walkin.get("headline", "Match in Progress")
    story = walkin.get("story", "")
    what_matters = walkin.get("what_matters_now", "")
    watch_player = walkin.get("watch_this_player", {})
    room_mood = walkin.get("room_mood", "Hyped")
    join_line = walkin.get("join_line", "Jump in!")

    st.markdown(f"""
    <div style="padding:4px 0">
        <div style="font-size:19px;font-weight:800;color:var(--text-main);margin-bottom:6px">{headline}</div>
        <div style="font-size:13px;color:var(--text-muted);line-height:1.5;margin-bottom:10px">{story}</div>
        
        <div style="margin-bottom:10px;background:var(--chat-bg);padding:9px 12px;border-radius:12px;border-left:3px solid var(--accent-gold)">
            <span style="font-size:10px;font-weight:800;color:var(--accent-gold);text-transform:uppercase">What Matters Now</span>
            <div style="font-size:12px;color:var(--text-main);font-weight:600;margin-top:2px">{what_matters}</div>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">
            <span class="pill-chip pill-blue">👀 {watch_player.get("name", "")}: {watch_player.get("why", "")}</span>
            <span class="pill-chip pill-amber">🎭 Room Mood: {room_mood}</span>
        </div>

        <div style="font-size:13px;color:var(--text-main);font-weight:800;margin-bottom:14px">{join_line}</div>

        <div style="display:flex;justify-content:space-between;color:var(--text-sub);font-size:10px;margin-bottom:10px">
            <span>📖 Read in 20 seconds</span>
            <span>as of over {snap_over}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="d11-primary-btn">', unsafe_allow_html=True)
    if st.button("🏏 Join Watch-Along Stream", key="modal_join_btn", use_container_width=True):
        st.toast("🎉 Joining the watch-along stream! (demo)", icon="🏏")
    st.markdown('</div>', unsafe_allow_html=True)


# ── A. Branded Top Navigation ──────────────────────────────────
st.markdown(f"""
<div class="top-nav">
    <div class="brand-badge">
        {get_d11_shield_svg(26)}
        <div class="d11-logo-text">
            <span>DREAM11</span>
            <span class="watchalong-tag">Watch Along</span>
        </div>
    </div>
    <div class="live-pulse-pill">● LIVE REPLAY</div>
</div>
""", unsafe_allow_html=True)

# Theme and Language Toggle Bar
col_theme, col_lang_ctrl = st.columns([1, 1])
with col_theme:
    selected_theme = st.selectbox(
        "Theme", ["🌙 Dark Stadium", "☀️ Light Arena"],
        index=0 if is_dark else 1,
        key="theme_selector",
        label_visibility="collapsed"
    )
    theme_val = "dark" if "Dark" in selected_theme else "light"
    if theme_val != st.session_state.theme:
        st.session_state.theme = theme_val
        st.rerun()

with col_lang_ctrl:
    selected_lang = st.selectbox(
        "Language", ["🇬🇧 English", "🇮🇳 Hinglish"],
        index=0 if st.session_state.language == "english" else 1,
        key="lang_selector",
        label_visibility="collapsed"
    )
    lang_val = "english" if "English" in selected_lang else "hinglish"
    if lang_val != st.session_state.language:
        st.session_state.language = lang_val
        st.rerun()


# ── B. Live Scoreboard Card ────────────────────────────────────
bidx = st.session_state.ball_idx
current_ball = balls[bidx]
current_state = state_at(bidx, balls, tensions, moments)

batting_team = current_ball["team_batting"]
bowling_team = "India" if batting_team == "Pakistan" else "Pakistan"

st.markdown('<div class="d11-card">', unsafe_allow_html=True)

c_left, c_right = st.columns([1, 1])
with c_left:
    st.markdown(f'''
    <div style="display:flex;align-items:center;gap:7px;margin-bottom:2px">
        {get_team_crest_svg(batting_team, 18)}
        <span style="font-size:14px;font-weight:800;color:var(--text-main)">{batting_team}</span>
        <span class="pill-chip pill-red" style="font-size:9px;padding:1px 6px">BATTING</span>
    </div>
    <div class="score-hero">{current_ball["cum_runs"]}/{current_ball["cum_wkts"]}</div>
    <div class="score-sub">Overs: {current_ball["display_over"]} (Inn {current_ball["innings"]})</div>
    ''', unsafe_allow_html=True)

with c_right:
    if current_ball["innings"] == 2:
        st.markdown(f'''
        <div class="target-glow">🎯 Target: {current_ball["target"]}</div>
        <div style="font-size:12px;font-weight:700;color:var(--text-main)">Need {current_ball["runs_needed"]} off {current_ball["balls_left"]}b</div>
        <div class="score-sub" style="margin-top:2px">CRR: {current_state["crr"]} | RRR: {current_state.get("rrr", "-")}</div>
        ''', unsafe_allow_html=True)
    else:
        proj = current_state.get("projected_score", "")
        st.markdown(f'''
        <div class="target-glow">📊 Projected: {proj}</div>
        <div class="score-sub" style="margin-top:2px">CRR: {current_state["crr"]}</div>
        <div class="score-sub">Balls left: {current_ball["balls_left"]}</div>
        ''', unsafe_allow_html=True)

# Last 12 deliveries chips
last_12 = current_state.get("last_12", [])
chips_html = ''.join([get_ball_chip_html(b) for b in last_12])
st.markdown(f'<div style="margin-top:9px;display:flex;align-items:center;gap:1px;overflow-x:auto;padding-bottom:2px">{chips_html}</div>', unsafe_allow_html=True)

# Chase meter (second innings)
if current_ball["innings"] == 2 and current_state.get("chase_meter") is not None:
    cm_pct = current_state["chase_meter"]
    grad = get_chase_gradient(cm_pct)
    st.markdown(f'''
    <div style="margin-top:10px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:11px;font-weight:800;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px">Chase Meter</span>
            <span style="font-size:14px;font-weight:800;color:var(--text-main)">{cm_pct:.0f}%</span>
        </div>
        <div class="chase-bar-bg">
            <div class="chase-bar-fill" style="width:{cm_pct}%;background:{grad}"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-sub);font-weight:600">
            <span>{bowling_team}</span>
            <span>{batting_team}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── C. Match Clock Replay Control ──────────────────────────────
st.markdown('<div class="d11-card">', unsafe_allow_html=True)
inn_label = f"Innings {current_ball['innings']}"
phase_label = current_state.get("phase", "")

st.markdown(f'''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
    <span style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase">⏱ MATCH CLOCK</span>
    <span class="pill-chip pill-muted">{inn_label} • {current_ball["display_over"]} ov • {phase_label}</span>
</div>
''', unsafe_allow_html=True)

new_idx = st.slider(
    f"{inn_label}, {current_ball['display_over']} ov",
    min_value=0,
    max_value=len(balls) - 1,
    value=st.session_state.ball_idx,
    key="slider_clock",
    label_visibility="collapsed",
)
if new_idx != st.session_state.ball_idx:
    st.session_state.ball_idx = new_idx
    st.rerun()

# Playback controls
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    if st.button("⏮", help="Restart match"):
        st.session_state.ball_idx = 0
        st.session_state.playing = False
        st.rerun()
with b2:
    play_icon = "⏸" if st.session_state.playing else "▶"
    if st.button(play_icon, help="Play / Pause Replay"):
        st.session_state.playing = not st.session_state.playing
        st.rerun()
with b3:
    speeds = ["1x", "2x", "5x"]
    idx_spd = speeds.index(st.session_state.speed) if st.session_state.speed in speeds else 0
    if st.button(f"⚡{st.session_state.speed}", help="Replay speed"):
        st.session_state.speed = speeds[(idx_spd + 1) % len(speeds)]
        st.rerun()
with b4:
    if st.button("🎯 Next", help="Next big turning point"):
        for m in moments:
            if m["ball_idx"] > st.session_state.ball_idx:
                st.session_state.ball_idx = m["ball_idx"]
                st.session_state.playing = False
                st.rerun()
                break
with b5:
    if st.button("🔥 Last 2", help="Jump to Death Overs"):
        for i, b in enumerate(balls):
            if b["innings"] == 2 and b["over"] >= 18:
                st.session_state.ball_idx = i
                st.session_state.playing = False
                st.rerun()
                break

# Quick-jump buttons
inn2_start = next((i for i, b in enumerate(balls) if b["innings"] == 2), 0)
col_q1, col_q2 = st.columns(2)
with col_q1:
    if st.button("🏁 Start of Chase", use_container_width=True):
        st.session_state.ball_idx = inn2_start
        st.session_state.playing = False
        st.rerun()
with col_q2:
    if st.button("⚡ Over 19.3 (Kohli Six)", use_container_width=True):
        st.session_state.ball_idx = 245
        st.session_state.playing = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── D. Tension Card (Feature: Wake Me When It Matters) ──────────
st.markdown('<div class="d11-card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase">⚡ WAKE ME WHEN IT MATTERS</span>
    <span class="pill-chip pill-red">Tension Radar</span>
</div>
''', unsafe_allow_html=True)

# Plotly Tension Chart
chart_x = list(range(bidx + 1))
chart_y = smoothed[:bidx + 1]

hover_texts = []
for i in range(bidx + 1):
    b = balls[i]
    txt = f"Over {b['display_over']}<br>{b['team_batting']} {b['cum_runs']}/{b['cum_wkts']}"
    if b['is_wicket']:
        txt += f"<br>WICKET: {b['player_out']}"
    elif b['runs_batter'] == 6:
        txt += f"<br>SIX by {b['batter']}"
    elif b['runs_batter'] == 4:
        txt += f"<br>FOUR by {b['batter']}"
    hover_texts.append(txt)

fig = go.Figure()
area_fill_color = 'rgba(225, 29, 72, 0.22)' if is_dark else 'rgba(217, 30, 43, 0.12)'

fig.add_trace(go.Scatter(
    x=chart_x, y=chart_y,
    fill='tozeroy',
    fillcolor=area_fill_color,
    line=dict(color='#E11D48', width=2.2),
    hovertext=hover_texts,
    hoverinfo='text',
    name='Tension',
))

# Key Moment Pins
for m in moments:
    if m["ball_idx"] <= bidx:
        fig.add_trace(go.Scatter(
            x=[m["ball_idx"]],
            y=[smoothed[m["ball_idx"]]],
            mode='markers+text',
            marker=dict(size=12, color='#F5B301', symbol='diamond', line=dict(width=1, color='#FFFFFF')),
            text=[str(m["rank"])],
            textposition='top center',
            textfont=dict(size=10, color='#F5B301', family='Plus Jakarta Sans', weight=800),
            hovertext=f"#{m['rank']}: {m['reason']}",
            hoverinfo='text',
            showlegend=False,
        ))

# Cursor and Innings separator
fig.add_vline(x=bidx, line_dash="dot", line_color="#94A3B8", line_width=1.2)
if inn2_start > 0:
    fig.add_vline(x=inn2_start, line_dash="dash", line_color="rgba(148, 163, 184, 0.4)", line_width=1,
                  annotation_text="Chase", annotation_position="top",
                  annotation_font_size=9, annotation_font_color="#94A3B8")

fig.update_layout(
    height=185,
    margin=dict(l=0, r=0, t=10, b=22),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, len(balls) - 1]),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 105]),
    showlegend=False,
    hovermode='x unified',
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Fan Preferences
st.markdown('<div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">Fan Alert Preferences</div>', unsafe_allow_html=True)
col_team, col_player, col_sens = st.columns(3)
with col_team:
    fav_team = st.selectbox("Fav Team", ["India", "Pakistan"], index=0 if st.session_state.fav_team == "India" else 1, key="fav_team_key", label_visibility="collapsed")
    if fav_team != st.session_state.fav_team:
        st.session_state.fav_team = fav_team
        st.rerun()
with col_player:
    fav_player = st.selectbox("Fav Player", all_star_names, index=all_star_names.index(st.session_state.fav_player) if st.session_state.fav_player in all_star_names else 0, key="fav_player_key", label_visibility="collapsed")
    if fav_player != st.session_state.fav_player:
        st.session_state.fav_player = fav_player
        st.rerun()
with col_sens:
    sensitivity = st.selectbox("Sensitivity", ["Calm", "Normal", "Hyped"], index=["Calm", "Normal", "Hyped"].index(st.session_state.sensitivity), key="sens_key", label_visibility="collapsed")
    if sensitivity != st.session_state.sensitivity:
        st.session_state.sensitivity = sensitivity
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── E. Smart Alert Feed ─────────────────────────────────────────
st.markdown('<div class="d11-card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase">🔔 SMART ALERTS FEED</span>
</div>
''', unsafe_allow_html=True)

active_alerts = [a for a in current_alerts if a["ball_idx"] <= bidx]
latest_alerts = active_alerts[-5:] if active_alerts else []

# Telemetry stats
total_so_far = bidx + 1
threshold = config.SENSITIVITY[st.session_state.sensitivity]
below_th = sum(1 for i in range(total_so_far) if tensions[i]["tension"] < threshold)
skip_pct = round(100 * below_th / total_so_far) if total_so_far > 0 else 0

c_s1, c_s2 = st.columns(2)
with c_s1:
    st.markdown(f'<div class="pill-chip pill-red">Alerts sent: {len(active_alerts)}</div>', unsafe_allow_html=True)
with c_s2:
    st.markdown(f'<div class="pill-chip pill-green">Safe to skip: {skip_pct}%</div>', unsafe_allow_html=True)

if not latest_alerts:
    st.markdown('''
    <div style="text-align:center;padding:16px;color:var(--text-sub)">
        <div style="font-size:22px;margin-bottom:4px">🔕</div>
        <div style="font-size:12px">All quiet. We will ping you when it matters.</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    for alert in reversed(latest_alerts):
        sev = alert["severity"]
        trigger = alert["trigger"]
        display_over = alert["display_over"]
        why_now = get_alert_line(alert["ball_idx"], st.session_state.language)
        if not why_now:
            from ai.fallbacks import generate_alert_line_fallback
            why_now = generate_alert_line_fallback(alert, st.session_state.language)

        pill_cls = "pill-red" if sev == "Hot" else ("pill-amber" if sev == "Rising" else "pill-green")
        st.markdown(f'''
        <div class="alert-box">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px">
                <div style="display:flex;align-items:center;gap:6px">
                    {get_d11_shield_svg(20)}
                    <span style="font-weight:800;font-size:12px;color:var(--text-main)">Dream11 Match alert</span>
                </div>
                <span class="pill-chip {pill_cls}">{sev}</span>
            </div>
            <div style="font-size:12px;color:var(--text-main);margin:3px 0 5px 0;line-height:1.4">{why_now}</div>
            <div style="font-size:11px;color:var(--text-sub);font-weight:600">Over {display_over} • {trigger.title()} • Just now</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="d11-primary-btn">', unsafe_allow_html=True)
    if st.button("🔴 Join Live Stream Now", key="join_live_feed_btn", use_container_width=True):
        st.toast("🎉 Joining watch-along stream! (demo)", icon="🏏")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── F. Walk-In Ready Card (Feature 1) ───────────────────────────
st.markdown('<div class="d11-card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase">🚶 WALK-IN READY</span>
    <span class="pill-chip pill-muted">20s Catch-Up</span>
</div>
''', unsafe_allow_html=True)

cur_over = current_ball["over"]
cur_inn = current_ball["innings"]
walkin_card, snap_over = get_walkin_for_over(cur_inn, cur_over, st.session_state.language)

col_w1, col_w2 = st.columns(2)
with col_w1:
    st.markdown('<div class="d11-primary-btn">', unsafe_allow_html=True)
    if st.button("🔴 Walk me in", key="trigger_walkin_modal", use_container_width=True):
        show_walkin_modal(walkin_card, snap_over)
    st.markdown('</div>', unsafe_allow_html=True)

with col_w2:
    toggle_txt = "Hide Card" if st.session_state.show_walkin_card else "View Inline"
    if st.button(toggle_txt, key="toggle_walkin_inline_btn", use_container_width=True):
        st.session_state.show_walkin_card = not st.session_state.show_walkin_card
        st.rerun()

# Inline expansion
if st.session_state.show_walkin_card and walkin_card:
    headline = walkin_card.get("headline", "Match in Progress")
    story = walkin_card.get("story", "")
    what_matters = walkin_card.get("what_matters_now", "")
    watch_player = walkin_card.get("watch_this_player", {})
    room_mood = walkin_card.get("room_mood", "Hyped")
    join_line = walkin_card.get("join_line", "Jump in!")

    st.markdown(f'''
    <div style="background:var(--chat-bg);border:1.5px solid var(--accent-red);border-radius:14px;padding:12px;margin-top:10px">
        <div style="font-size:16px;font-weight:800;color:var(--text-main);margin-bottom:5px">{headline}</div>
        <div style="font-size:12px;color:var(--text-muted);line-height:1.5;margin-bottom:8px">{story}</div>

        <div style="margin-bottom:8px;background:var(--card-bg-solid);padding:7px 10px;border-radius:8px;border-left:3px solid var(--accent-gold)">
            <span style="font-size:10px;font-weight:800;color:var(--accent-gold);text-transform:uppercase">What Matters Now</span>
            <div style="font-size:12px;color:var(--text-main);font-weight:600">{what_matters}</div>
        </div>

        <div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px">
            <span class="pill-chip pill-blue">👀 {watch_player.get("name", "")}: {watch_player.get("why", "")}</span>
            <span class="pill-chip pill-amber">🎭 {room_mood}</span>
        </div>

        <div style="font-size:12px;color:var(--text-main);font-weight:800;margin-bottom:10px">{join_line}</div>

        <div style="display:flex;justify-content:space-between;color:var(--text-sub);font-size:10px;margin-bottom:8px">
            <span>📖 Read in 20 seconds</span>
            <span>as of over {snap_over}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="d11-primary-btn">', unsafe_allow_html=True)
    if st.button("🏏 Join the Watch Along", key="join_walkin_inline_btn", use_container_width=True):
        st.toast("🎉 Joining watch-along stream! (demo)", icon="🏏")
    st.markdown('</div>', unsafe_allow_html=True)

# Ball 0 Pre-Match Card
if bidx == 0:
    st.markdown(f'''
    <div style="text-align:center;padding:12px;background:var(--chat-bg);border-radius:12px;border:1px solid var(--card-border);margin-top:8px">
        <div style="font-size:15px;font-weight:800;color:var(--text-main);margin-bottom:2px">🏏 {config.MATCH_TITLE}</div>
        <div class="score-sub">{config.MATCH_VENUE} • {config.MATCH_DATE}</div>
        <div style="margin-top:6px;font-size:12px;color:var(--accent-gold);font-weight:700">Toss: Pakistan won and opted to bat • Match about to begin!</div>
    </div>
    ''', unsafe_allow_html=True)

# Innings Break Card
if current_ball["innings"] == 2 and bidx == inn2_start:
    inn1_balls = [b for b in balls if b["innings"] == 1]
    inn1_total = inn1_balls[-1]["cum_runs"] if inn1_balls else 0
    inn1_wkts = inn1_balls[-1]["cum_wkts"] if inn1_balls else 0
    best_moment = moments[0] if moments and moments[0]["innings"] == 1 else None
    best_txt = best_moment["reason"] if best_moment else "Action in death overs"
    st.markdown(f'''
    <div style="text-align:center;padding:12px;background:var(--chat-bg);border-radius:12px;border:1px solid var(--accent-gold);margin-top:8px">
        <span class="pill-chip pill-amber" style="margin-bottom:4px">INNINGS BREAK</span>
        <div style="font-size:18px;font-weight:800;color:var(--text-main);margin:3px 0">Target: {inn1_total + 1} for India</div>
        <div class="score-sub">Pakistan finished at {inn1_total}/{inn1_wkts} in 20 overs</div>
        <div style="font-size:11px;color:var(--text-main);margin-top:4px">Innings 1 Landmark: <b>{best_txt}</b></div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── G. Chat Rewind & Vibe Meter (Feature 2) ────────────────────
st.markdown('<div class="d11-card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
    <span style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase">💬 CHAT REWIND & VIBE METER</span>
</div>
''', unsafe_allow_html=True)

vibe, vibe_snap = get_vibe_for_over(current_ball["innings"], current_ball["over"])

if vibe:
    mood_val = vibe.get("mood", 50)
    mood_label = vibe.get("mood_label", "Chilling")
    themes = vibe.get("themes", [])
    hottest_id = vibe.get("hottest_take", None)
    banter_tone = vibe.get("banter_tone", "Playful")
    abuse_count_total = sum(
        v.get("abuse_count", 0) for v in vibes_data
        if (v.get("innings", 1) < current_ball["innings"]) or
           (v.get("innings", 1) == current_ball["innings"] and v.get("over", 99) <= current_ball["over"])
    )

    # Semicircle Mood Gauge
    gauge_font_color = "#FFFFFF" if is_dark else "#0F172A"
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mood_val,
        title={'text': mood_label, 'font': {'size': 13, 'color': gauge_font_color, 'family': 'Plus Jakarta Sans'}},
        number={'font': {'size': 26, 'color': gauge_font_color, 'family': 'Plus Jakarta Sans', 'weight': 800}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)'},
            'bar': {'color': '#E11D48', 'thickness': 0.28},
            'bgcolor': 'rgba(0,0,0,0.1)' if not is_dark else '#23232C',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 33], 'color': '#065F46' if is_dark else '#A7F3D0'},
                {'range': [33, 66], 'color': '#78350F' if is_dark else '#FDE68A'},
                {'range': [66, 100], 'color': '#881337' if is_dark else '#FECDD3'},
            ],
            'shape': 'angular',
        }
    ))
    gauge_fig.update_layout(
        height=145,
        margin=dict(l=15, r=15, t=25, b=5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(gauge_fig, use_container_width=True, config={'displayModeBar': False})

    # Theme Chips
    theme_chips_html = ''.join([f'<span class="pill-chip pill-blue">{t}</span>' for t in themes[:3]])
    st.markdown(f'<div style="margin-bottom:8px;display:flex;gap:4px;flex-wrap:wrap">{theme_chips_html}</div>', unsafe_allow_html=True)

    # Hottest Take Card
    hottest_msg = next((m for m in chat_data if m["id"] == hottest_id), None)
    if hottest_msg:
        st.markdown(f'''
        <div class="d11-card-gold">
            <div style="font-size:10px;color:var(--accent-gold);font-weight:800;margin-bottom:2px">🔥 HOTTEST TAKE</div>
            <div style="font-size:11px;font-weight:700;color:#38BDF8">{hottest_msg["handle"]}</div>
            <div style="font-size:12px;color:var(--text-main);font-weight:500">{hottest_msg["text"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    # Banter Tone & Abuse Blocked
    st.markdown(f'''
    <div style="display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap;align-items:center">
        <span class="pill-chip {"pill-amber" if banter_tone == "Heated" else "pill-green"}">{banter_tone} Tone</span>
        <span class="pill-chip pill-muted">🛡 Banter Guard: {abuse_count_total} blocked</span>
    </div>
    ''', unsafe_allow_html=True)

# Latest 15 simulated messages
chat_up_to = [m for m in chat_data if m["ball_idx"] <= bidx]
latest_chat = chat_up_to[-15:] if chat_up_to else []

if not latest_chat:
    st.markdown('<div class="score-sub" style="text-align:center;padding:12px">Chat will appear as deliveries are bowled...</div>', unsafe_allow_html=True)
else:
    for msg in latest_chat:
        is_abuse = msg.get("type") == "abuse"
        is_pinned = msg.get("is_pinned", False) or msg.get("type") == "shoutout"
        db = msg.get("dreambucks", 0)

        if is_abuse:
            st.markdown(f'''
            <details class="abuse-guard">
                <summary>🛡 Message hidden by Banter Guard <span style="color:#38BDF8;font-size:10px;margin-left:4px">[Tap to Show]</span></summary>
                <div style="margin-top:4px;padding-top:4px;border-top:1px solid var(--chat-border);color:var(--text-sub);font-style:italic;font-size:11px">
                    <span style="font-weight:700;color:#38BDF8">{msg["handle"]}:</span> {msg["text"]}
                </div>
            </details>
            ''', unsafe_allow_html=True)
        elif is_pinned:
            st.markdown(f'''
            <div class="chat-bubble-pinned">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
                    <span style="font-weight:700;color:#38BDF8;font-size:11px">{msg["handle"]}</span>
                    {"<span style='color:var(--accent-gold);font-weight:800;font-size:11px'>💰 " + str(db) + " DreamBucks</span>" if db > 0 else ""}
                </div>
                <div style="color:var(--text-main);font-size:12px">{msg["text"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-bubble">
                <span style="font-weight:700;color:#38BDF8;font-size:11px">{msg["handle"]}:</span>
                <span style="color:var(--text-main);font-size:12px"> {msg["text"]}</span>
            </div>
            ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── H. Footer & Information ────────────────────────────────────
st.markdown('''
<div class="d11-footer">
    Simulated chat for demonstration purposes.<br>
    Independent prototype inspired by public information about Dream11 Watch Along.<br>
    Not an official Dream11 product.
</div>
''', unsafe_allow_html=True)

with st.expander("ℹ️ How Watch-Along Copilot works"):
    st.markdown("""
    **Core Architectural Principles:**
    1. **Deterministic Logic**: Chase Meter and Tension per ball calculate purely through calibrated Python formulas.
    2. **Logistic Chase Meter**: Modeled using:
       $$\\text{pressure} = \\text{RRR} - \\text{Par}(\\text{wickets in hand})$$
       $$\\text{Chase} = \\frac{1}{1 + e^{0.45 \\times \\text{pressure}}}$$
    3. **Tension Score**:
       $$\\text{raw} = 0.9 \\times \\text{swing} + \\text{event\\_pts} \\times \\text{phase\\_mult} + \\text{closeness}$$
       $$\\text{tension} = \\text{clamp}\\left(100 \\times \\frac{\\text{raw}}{\\text{P95}}, 0, 100\\right) + \\text{star\\_bonus}$$
    4. **Smart Alerts**: Filter deliveries using sensitivity thresholds (Calm=75, Normal=60, Hyped=45) with minimum pacing intervals.
    5. **AI Synthesis**: Claude summarizes watch-along chat vibe and builds 20-second catch-ups, strictly constrained to facts passed by code.
    """)


# ── Auto-play Loop ─────────────────────────────────────────────
if st.session_state.playing and st.session_state.ball_idx < len(balls) - 1:
    speed_delay = config.PLAY_SPEED.get(st.session_state.speed, 1.0)
    time.sleep(speed_delay)
    st.session_state.ball_idx += 1
    st.rerun()
elif st.session_state.playing and st.session_state.ball_idx >= len(balls) - 1:
    st.session_state.playing = False
