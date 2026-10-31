"""
Watch-Along Copilot - Dream11 FDE Intern Assignment
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
    page_title="Watch-Along Copilot",
    page_icon="🏏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Global Mobile-first styling */
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
.main .block-container {
    max-width: 430px !important;
    padding: 0.5rem 0.75rem 2rem 0.75rem !important;
    margin: 0 auto !important;
}
.stApp {
    background-color: #0F0F12 !important;
    color: #FFFFFF !important;
}

@media (max-width: 430px) {
    .main .block-container {
        padding: 0.25rem 0.5rem 1.5rem 0.5rem !important;
    }
}

/* Cards */
.card {
    background: #1A1A1F;
    border: 1px solid #2A2A31;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.card-gold {
    background: #1A1A1F;
    border: 1.5px solid #F5B301;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
}

/* Header */
.header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 2px 0;
}
.header-title {
    font-size: 17px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.2px;
}
.live-pill {
    background: #D91E2B;
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 12px;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    animation: live-pulse 2s infinite ease-in-out;
}
@keyframes live-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.82; transform: scale(0.98); }
}

/* Scoreboard */
.score-main {
    font-size: 30px;
    font-weight: 800;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.score-label {
    font-size: 11px;
    color: #9A9AA6;
    font-weight: 500;
}
.team-name {
    font-size: 14px;
    font-weight: 700;
    color: #FFFFFF;
}
.target-line {
    font-size: 13px;
    color: #F59E0B;
    font-weight: 700;
}

/* Ball chips */
.ball-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 25px;
    height: 25px;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
    margin: 1px;
    font-variant-numeric: tabular-nums;
}
.ball-0 { background: #2A2A31; color: #9A9AA6; }
.ball-1, .ball-2, .ball-3 { background: #272730; color: #FFFFFF; border: 1px solid #3A3A44; }
.ball-4 { background: #1E3A8A; color: #93C5FD; font-weight: 800; }
.ball-6 { background: #78350F; color: #F5B301; font-weight: 800; }
.ball-W { background: #7F1D1D; color: #FF4D4D; font-weight: 800; }
.ball-dot { background: #222228; color: #6B7280; }

/* Chase meter */
.chase-bar-bg {
    width: 100%;
    height: 8px;
    background: #2A2A31;
    border-radius: 4px;
    overflow: hidden;
    margin: 5px 0 3px 0;
}
.chase-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

/* Alert notifications */
.alert-card {
    background: #151519;
    border: 1px solid #2A2A31;
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.alert-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}
.alert-icon-title {
    display: flex;
    align-items: center;
    gap: 6px;
}
.alert-icon {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: #D91E2B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
}

/* Pills & Chips */
.pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 700;
    margin: 1px;
    letter-spacing: 0.2px;
}
.pill-red { background: #7F1D1D; color: #FF4D4D; }
.pill-amber { background: #78350F; color: #F59E0B; }
.pill-green { background: #14532D; color: #22C55E; }
.pill-blue { background: #1E3A5F; color: #60A5FA; }
.pill-gold { background: #78350F; color: #F5B301; }
.pill-muted { background: #2A2A31; color: #9A9AA6; }

/* Chat message */
.chat-msg {
    padding: 6px 10px;
    margin: 4px 0;
    border-radius: 10px;
    background: #151519;
    font-size: 12px;
    border: 1px solid #24242C;
}
.chat-msg-pinned {
    padding: 6px 10px;
    margin: 4px 0;
    border-radius: 10px;
    background: #1A1A1F;
    font-size: 12px;
    border: 1.5px solid #F5B301;
}
.chat-handle {
    font-weight: 700;
    color: #60A5FA;
    font-size: 11px;
}
.chat-text {
    color: #E2E8F0;
    font-size: 12px;
}
.dreambucks {
    color: #F5B301;
    font-weight: 700;
    font-size: 11px;
}

/* Banter Guard collapsed disclosure */
details.abuse-guard {
    background: #141418;
    border: 1px dashed #3F3F46;
    border-radius: 8px;
    padding: 6px 8px;
    margin: 4px 0;
}
details.abuse-guard summary {
    cursor: pointer;
    color: #9A9AA6;
    font-size: 11px;
    font-weight: 600;
    user-select: none;
    outline: none;
}
details.abuse-guard summary:hover {
    color: #D4D4D8;
}
.abuse-revealed {
    margin-top: 4px;
    padding-top: 4px;
    border-top: 1px solid #27272A;
    color: #71717A;
    font-style: italic;
    font-size: 11px;
}

/* Streamlit Button Tweaks */
div.stButton > button {
    border-radius: 14px;
    font-weight: 700;
    font-size: 13px;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    border-color: #D91E2B;
}

/* Primary red button */
.btn-primary-red div.stButton > button {
    background: #D91E2B !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 10px rgba(217, 30, 43, 0.35);
}

/* Section label */
.section-label {
    font-size: 11px;
    font-weight: 800;
    color: #9A9AA6;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* Footer text */
.footer-text {
    font-size: 10px;
    color: #71717A;
    text-align: center;
    padding: 12px 0 4px 0;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)


# ── Load data (cached) ────────────────────────────────────────
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

# All star player names
all_star_names = [p["name"] for p in stars["batters"]] + [p["name"] for p in stars["bowlers"]]

# ── Session state ──────────────────────────────────────────────
if "ball_idx" not in st.session_state:
    st.session_state.ball_idx = 0
if "playing" not in st.session_state:
    st.session_state.playing = False
if "speed" not in st.session_state:
    st.session_state.speed = "1x"
if "language" not in st.session_state:
    st.session_state.language = "english"
if "fav_team" not in st.session_state:
    st.session_state.fav_team = "India"
if "fav_player" not in st.session_state:
    st.session_state.fav_player = all_star_names[0] if all_star_names else "V Kohli"
if "sensitivity" not in st.session_state:
    st.session_state.sensitivity = "Normal"
if "show_walkin_card" not in st.session_state:
    st.session_state.show_walkin_card = False

# Compute tension with favourite player
@st.cache_data
def get_tensions(fav_player):
    return compute_tension(balls, fav_player)

tensions = get_tensions(st.session_state.fav_player)
smoothed = smooth_tension(tensions)
moments = find_key_moments(tensions, balls)

# Generate alerts for current sensitivity
@st.cache_data
def get_alerts_for_sensitivity(sensitivity, fav_player):
    t = compute_tension(balls, fav_player)
    return generate_alerts(balls, t, sensitivity)

current_alerts = get_alerts_for_sensitivity(st.session_state.sensitivity, st.session_state.fav_player)


# ── Helper functions ───────────────────────────────────────────
def get_ball_chip_html(val):
    """Return HTML for a ball chip."""
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


def get_chase_color(pct):
    """Get color for chase meter fill."""
    if pct >= 55:
        return "#22C55E"
    elif pct >= 40:
        return "#F59E0B"
    else:
        return "#D91E2B"


def get_walkin_for_over(innings, over, language):
    """Get Walk-In Ready data for nearest over."""
    for w in walkins_data:
        if w.get("innings") == innings and w.get("over") == over and w.get("language") == language:
            return w, over
    closest = None
    min_dist = float('inf')
    for w in walkins_data:
        if w.get("innings") == innings and w.get("language") == language:
            dist = abs(w.get("over", 0) - over)
            if dist < min_dist:
                min_dist = dist
                closest = w
    snap_over = closest.get("over", over) if closest else over
    return closest, snap_over


def get_vibe_for_over(innings, over):
    """Get vibe data for nearest over."""
    for v in vibes_data:
        if v.get("innings", 1) == innings and v.get("over") == over:
            return v, over
    closest = None
    min_dist = float('inf')
    for v in vibes_data:
        if v.get("innings", 1) == innings:
            dist = abs(v.get("over", 0) - over)
            if dist < min_dist:
                min_dist = dist
                closest = v
    snap_over = closest.get("over", over) if closest else over
    return closest, snap_over


def get_alert_line(ball_idx, language):
    """Get cached alert why-now line."""
    for a in alerts_cache:
        if a["ball_idx"] == ball_idx and a.get("language", "english") == language:
            return a.get("why_now", "")
    for a in alerts_cache:
        if a["ball_idx"] == ball_idx:
            return a.get("why_now", "")
    return ""


# ── Dialog for Walk-In Ready ───────────────────────────────────
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

    mood_colors = {
        "Nervous": "#F59E0B", "Hyped": "#22C55E", "Heartbreak": "#D91E2B",
        "Chilling": "#60A5FA", "Roasting": "#FF4D4D", "Electric": "#F5B301",
    }
    mood_color = mood_colors.get(room_mood, "#22C55E")

    st.markdown(f"""
    <div style="margin-bottom:10px">
        <div style="font-size:18px;font-weight:800;color:#FFFFFF;margin-bottom:6px">{headline}</div>
        <div style="font-size:13px;color:#E2E8F0;line-height:1.5;margin-bottom:10px">{story}</div>
        
        <div style="margin-bottom:10px;background:#151519;padding:8px 12px;border-radius:10px;border-left:3px solid #F59E0B">
            <span style="font-size:10px;font-weight:700;color:#9A9AA6;text-transform:uppercase">What Matters Now</span>
            <div style="font-size:12px;color:#F59E0B;font-weight:600;margin-top:2px">{what_matters}</div>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
            <span class="pill pill-blue">👀 {watch_player.get("name", "")}: {watch_player.get("why", "")}</span>
            <span class="pill" style="background:{mood_color}25;color:{mood_color}">🎭 {room_mood}</span>
        </div>

        <div style="font-size:13px;color:#FFFFFF;font-weight:700;margin-bottom:12px">{join_line}</div>

        <div style="display:flex;justify-content:space-between;color:#71717A;font-size:10px">
            <span>📖 Read in 20 seconds</span>
            <span>as of over {snap_over}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏏 Join the Watch Along", key="modal_join_btn", use_container_width=True):
        st.toast("🎉 Joining the watch-along! (demo)", icon="🏏")


# ── A. Header ──────────────────────────────────────────────────
col_title, col_live, col_lang = st.columns([5, 3, 3])
with col_title:
    st.markdown('<div class="header-title">🏏 Watch-Along Copilot</div>', unsafe_allow_html=True)
with col_live:
    st.markdown('<div style="text-align:right;padding-top:2px"><span class="live-pill">● LIVE REPLAY</span></div>', unsafe_allow_html=True)
with col_lang:
    selected_lang = st.selectbox(
        "Language",
        ["English", "Hinglish"],
        index=0 if st.session_state.language == "english" else 1,
        key="lang_select",
        label_visibility="collapsed"
    )
    if selected_lang.lower() != st.session_state.language:
        st.session_state.language = selected_lang.lower()
        st.rerun()


# ── B. Scoreboard ─────────────────────────────────────────────
bidx = st.session_state.ball_idx
current_ball = balls[bidx]
current_state = state_at(bidx, balls, tensions, moments)

team_colors = {"India": "#1E40AF", "Pakistan": "#14532D"}
batting_team = current_ball["team_batting"]
bowling_team = "India" if batting_team == "Pakistan" else "Pakistan"

st.markdown('<div class="card">', unsafe_allow_html=True)

# Team and score row
c1, c2 = st.columns([1, 1])
with c1:
    color = team_colors.get(batting_team, "#D91E2B")
    st.markdown(f'''
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">
        <div style="width:10px;height:10px;border-radius:50%;background:{color}"></div>
        <span class="team-name">{batting_team}</span>
        <span class="pill pill-red" style="font-size:9px">BAT</span>
    </div>
    <div class="score-main">{current_ball["cum_runs"]}/{current_ball["cum_wkts"]}</div>
    <div class="score-label">Overs: {current_ball["display_over"]} (Inn {current_ball["innings"]})</div>
    ''', unsafe_allow_html=True)
with c2:
    if current_ball["innings"] == 2:
        st.markdown(f'''
        <div class="target-line">Target: {current_ball["target"]}</div>
        <div class="score-label">Need {current_ball["runs_needed"]} off {current_ball["balls_left"]}b</div>
        <div class="score-label" style="margin-top:2px">CRR: {current_state["crr"]} | RRR: {current_state.get("rrr", "-")}</div>
        ''', unsafe_allow_html=True)
    else:
        proj = current_state.get("projected_score", "")
        st.markdown(f'''
        <div class="target-line">Projected: {proj}</div>
        <div class="score-label">CRR: {current_state["crr"]}</div>
        <div class="score-label" style="margin-top:2px">Balls left: {current_ball["balls_left"]}</div>
        ''', unsafe_allow_html=True)

# Last 12 balls chips
last_12 = current_state.get("last_12", [])
balls_html = ''.join([get_ball_chip_html(b) for b in last_12])
st.markdown(f'<div style="margin-top:8px;display:flex;align-items:center;gap:2px;overflow-x:auto">{balls_html}</div>', unsafe_allow_html=True)

# Chase meter (innings 2 only)
if current_ball["innings"] == 2 and current_state.get("chase_meter") is not None:
    cm_pct = current_state["chase_meter"]
    cm_color = get_chase_color(cm_pct)
    st.markdown(f'''
    <div style="margin-top:8px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span class="score-label" style="font-weight:700">Chase Meter</span>
            <span style="font-size:13px;font-weight:800;color:{cm_color}">{cm_pct:.0f}%</span>
        </div>
        <div class="chase-bar-bg">
            <div class="chase-bar-fill" style="width:{cm_pct}%;background:{cm_color}"></div>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span class="score-label">{bowling_team}</span>
            <span class="score-label">{batting_team}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── C. Match clock ─────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
innings_label = f"Innings {current_ball['innings']}"
phase_label = current_state.get("phase", "")
st.markdown(f'''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
    <span class="section-label">⏱ MATCH CLOCK</span>
    <span class="pill pill-muted">{innings_label} • {current_ball["display_over"]} ov • {phase_label}</span>
</div>
''', unsafe_allow_html=True)

# Slider
new_idx = st.slider(
    f"{innings_label}, {current_ball['display_over']} ov",
    min_value=0,
    max_value=len(balls) - 1,
    value=st.session_state.ball_idx,
    key="slider",
    label_visibility="collapsed",
)
if new_idx != st.session_state.ball_idx:
    st.session_state.ball_idx = new_idx
    st.rerun()

# Playback controls
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("⏮", help="Restart match"):
        st.session_state.ball_idx = 0
        st.session_state.playing = False
        st.rerun()
with c2:
    play_label = "⏸" if st.session_state.playing else "▶"
    if st.button(play_label, help="Play / Pause live replay"):
        st.session_state.playing = not st.session_state.playing
        st.rerun()
with c3:
    speed_options = ["1x", "2x", "5x"]
    curr_speed_idx = speed_options.index(st.session_state.speed) if st.session_state.speed in speed_options else 0
    if st.button(f"⚡{st.session_state.speed}", help="Replay speed"):
        st.session_state.speed = speed_options[(curr_speed_idx + 1) % len(speed_options)]
        st.rerun()
with c4:
    if st.button("🎯 Next", help="Next big moment"):
        for m in moments:
            if m["ball_idx"] > st.session_state.ball_idx:
                st.session_state.ball_idx = m["ball_idx"]
                st.session_state.playing = False
                st.rerun()
                break
with c5:
    if st.button("🔥 Last 2", help="Jump to last 2 overs"):
        for i, b in enumerate(balls):
            if b["innings"] == 2 and b["over"] >= 18:
                st.session_state.ball_idx = i
                st.session_state.playing = False
                st.rerun()
                break

# Start of chase quick jump
inn2_start = next((i for i, b in enumerate(balls) if b["innings"] == 2), 0)
col_chase, col_pp = st.columns([1, 1])
with col_chase:
    if st.button("🏁 Start of Chase", use_container_width=True):
        st.session_state.ball_idx = inn2_start
        st.session_state.playing = False
        st.rerun()
with col_pp:
    if st.button("⚡ Final Over", use_container_width=True):
        final_over_idx = next((i for i, b in enumerate(balls) if b["innings"] == 2 and b["over"] == 19), len(balls) - 7)
        st.session_state.ball_idx = final_over_idx
        st.session_state.playing = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── D. Tension card (Wake Me When It Matters) ──────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span class="section-label">⚡ WAKE ME WHEN IT MATTERS</span>
    <span class="pill pill-red">Tension Curve</span>
</div>
''', unsafe_allow_html=True)

# Tension chart - only up to current ball so it feels live
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

# Area fill
fig.add_trace(go.Scatter(
    x=chart_x, y=chart_y,
    fill='tozeroy',
    fillcolor='rgba(217, 30, 43, 0.16)',
    line=dict(color='#D91E2B', width=2),
    hovertext=hover_texts,
    hoverinfo='text',
    name='Tension',
))

# Key moment pins
for m in moments:
    if m["ball_idx"] <= bidx:
        fig.add_trace(go.Scatter(
            x=[m["ball_idx"]],
            y=[smoothed[m["ball_idx"]]],
            mode='markers+text',
            marker=dict(size=12, color='#F5B301', symbol='diamond', line=dict(width=1, color='#FFFFFF')),
            text=[str(m["rank"])],
            textposition='top center',
            textfont=dict(size=10, color='#F5B301', family='Inter'),
            hovertext=f"#{m['rank']}: {m['reason']}",
            hoverinfo='text',
            showlegend=False,
        ))

# Vertical cursor
fig.add_vline(x=bidx, line_dash="dot", line_color="#9A9AA6", line_width=1)

# Innings break line
if inn2_start > 0:
    fig.add_vline(x=inn2_start, line_dash="dash", line_color="#2A2A31", line_width=1,
                  annotation_text="Inn 2", annotation_position="top",
                  annotation_font_size=9, annotation_font_color="#9A9AA6")

fig.update_layout(
    height=190,
    margin=dict(l=0, r=0, t=10, b=25),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=False, zeroline=False, showticklabels=False,
        range=[0, len(balls) - 1],
    ),
    yaxis=dict(
        showgrid=False, zeroline=False, showticklabels=False,
        range=[0, 105],
    ),
    showlegend=False,
    hovermode='x unified',
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Fan settings
st.markdown('<div class="score-label" style="font-weight:700;margin-bottom:4px">Fan Alert Preferences</div>', unsafe_allow_html=True)
col_team, col_player, col_sens = st.columns(3)
with col_team:
    fav_team = st.selectbox(
        "Fav Team", ["India", "Pakistan"],
        index=0 if st.session_state.fav_team == "India" else 1,
        key="fav_team_sel",
        label_visibility="collapsed"
    )
    if fav_team != st.session_state.fav_team:
        st.session_state.fav_team = fav_team
        st.rerun()
with col_player:
    fav_player = st.selectbox(
        "Fav Player", all_star_names,
        index=all_star_names.index(st.session_state.fav_player) if st.session_state.fav_player in all_star_names else 0,
        key="fav_player_sel",
        label_visibility="collapsed"
    )
    if fav_player != st.session_state.fav_player:
        st.session_state.fav_player = fav_player
        st.rerun()
with col_sens:
    sensitivity = st.selectbox(
        "Sensitivity", ["Calm", "Normal", "Hyped"],
        index=["Calm", "Normal", "Hyped"].index(st.session_state.sensitivity),
        key="sens_sel",
        label_visibility="collapsed"
    )
    if sensitivity != st.session_state.sensitivity:
        st.session_state.sensitivity = sensitivity
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── E. Alert feed ──────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span class="section-label">🔔 SMART ALERTS FEED</span>
</div>
''', unsafe_allow_html=True)

active_alerts = [a for a in current_alerts if a["ball_idx"] <= bidx]
latest_alerts = active_alerts[-5:] if active_alerts else []

# Stats
total_balls_so_far = bidx + 1
threshold = config.SENSITIVITY[st.session_state.sensitivity]
below_threshold = sum(1 for i in range(total_balls_so_far) if tensions[i]["tension"] < threshold)
skip_pct = round(100 * below_threshold / total_balls_so_far) if total_balls_so_far > 0 else 0

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f'<div class="pill pill-red">Alerts sent: {len(active_alerts)}</div>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div class="pill pill-green">Safe to skip: {skip_pct}%</div>', unsafe_allow_html=True)

if not latest_alerts:
    st.markdown('''
    <div style="text-align:center;padding:16px;color:#9A9AA6">
        <div style="font-size:22px;margin-bottom:6px">🔕</div>
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

        pill_type = "red" if sev == "Hot" else ("amber" if sev == "Rising" else "green")
        
        st.markdown(f'''
        <div class="alert-card">
            <div class="alert-top">
                <div class="alert-icon-title">
                    <div class="alert-icon">🏏</div>
                    <span style="font-weight:700;font-size:12px;color:#FFFFFF">Dream11 Match alert</span>
                </div>
                <span class="pill pill-{pill_type}">{sev}</span>
            </div>
            <div style="font-size:12px;color:#E2E8F0;margin:4px 0 6px 0;line-height:1.4">{why_now}</div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="score-label">Over {display_over} • {trigger.title()} • Just now</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # Interactive Join Live button for alert feed
    st.markdown('<div class="btn-primary-red">', unsafe_allow_html=True)
    if st.button("🔴 Join Live Now", key="join_live_now_btn", use_container_width=True):
        st.toast("🎉 Joining the watch-along! (demo)", icon="🏏")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── F. Walk-In Ready ───────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span class="section-label">🚶 WALK-IN READY</span>
    <span class="pill pill-muted">20s Catch-Up</span>
</div>
''', unsafe_allow_html=True)

current_over = current_ball["over"]
current_innings = current_ball["innings"]
walkin_card, snap_over = get_walkin_for_over(current_innings, current_over, st.session_state.language)

col_walk_btn, col_inline_btn = st.columns([1, 1])
with col_walk_btn:
    st.markdown('<div class="btn-primary-red">', unsafe_allow_html=True)
    if st.button("🔴 Walk me in", key="walkin_modal_trigger", use_container_width=True):
        show_walkin_modal(walkin_card, snap_over)
    st.markdown('</div>', unsafe_allow_html=True)

with col_inline_btn:
    toggle_label = "Hide Card" if st.session_state.show_walkin_card else "View Inline"
    if st.button(toggle_label, key="toggle_inline_card", use_container_width=True):
        st.session_state.show_walkin_card = not st.session_state.show_walkin_card
        st.rerun()

# Inline card when requested
if st.session_state.show_walkin_card and walkin_card:
    headline = walkin_card.get("headline", "Match in Progress")
    story = walkin_card.get("story", "")
    what_matters = walkin_card.get("what_matters_now", "")
    watch_player = walkin_card.get("watch_this_player", {})
    room_mood = walkin_card.get("room_mood", "Hyped")
    join_line = walkin_card.get("join_line", "Jump in!")

    mood_colors = {
        "Nervous": "#F59E0B", "Hyped": "#22C55E", "Heartbreak": "#D91E2B",
        "Chilling": "#60A5FA", "Roasting": "#FF4D4D", "Electric": "#F5B301",
    }
    mood_color = mood_colors.get(room_mood, "#22C55E")

    st.markdown(f'''
    <div style="background:#151519;border:1.5px solid #D91E2B;border-radius:14px;padding:14px;margin-top:10px">
        <div style="font-size:17px;font-weight:800;color:#FFFFFF;margin-bottom:6px">{headline}</div>
        <div style="font-size:12px;color:#E2E8F0;line-height:1.5;margin-bottom:8px">{story}</div>

        <div style="margin-bottom:8px;background:#1F1F26;padding:8px 10px;border-radius:8px;border-left:3px solid #F59E0B">
            <span style="font-size:10px;font-weight:700;color:#9A9AA6;text-transform:uppercase">What Matters Now</span>
            <div style="font-size:12px;color:#F59E0B;font-weight:600">{what_matters}</div>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
            <span class="pill pill-blue">👀 {watch_player.get("name", "")}: {watch_player.get("why", "")}</span>
            <span class="pill" style="background:{mood_color}25;color:{mood_color}">🎭 {room_mood}</span>
        </div>

        <div style="font-size:13px;color:#FFFFFF;font-weight:700;margin-bottom:10px">{join_line}</div>

        <div style="display:flex;justify-content:space-between;color:#71717A;font-size:10px;margin-bottom:10px">
            <span>📖 Read in 20 seconds</span>
            <span>as of over {snap_over}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="btn-primary-red">', unsafe_allow_html=True)
    if st.button("🏏 Join the Watch Along", key="join_walkin_inline", use_container_width=True):
        st.toast("🎉 Joining the watch-along! (demo)", icon="🏏")
    st.markdown('</div>', unsafe_allow_html=True)

# Edge case: Ball 0 Pre-Match Card
if bidx == 0:
    st.markdown(f'''
    <div style="text-align:center;padding:12px;background:#151519;border-radius:12px;border:1px solid #2A2A31;margin-top:8px">
        <div style="font-size:15px;font-weight:800;color:#FFFFFF;margin-bottom:2px">🏏 {config.MATCH_TITLE}</div>
        <div class="score-label">{config.MATCH_VENUE} • {config.MATCH_DATE}</div>
        <div style="margin-top:6px;font-size:12px;color:#F59E0B;font-weight:700">Toss: Pakistan won and opted to bat • Match about to begin!</div>
    </div>
    ''', unsafe_allow_html=True)

# Edge case: Innings break card
if current_ball["innings"] == 2 and bidx == inn2_start:
    inn1_balls = [b for b in balls if b["innings"] == 1]
    inn1_total = inn1_balls[-1]["cum_runs"] if inn1_balls else 0
    inn1_wkts = inn1_balls[-1]["cum_wkts"] if inn1_balls else 0
    best_moment = moments[0] if moments and moments[0]["innings"] == 1 else None
    best_txt = best_moment["reason"] if best_moment else "High action in overs 15-20"
    st.markdown(f'''
    <div style="text-align:center;padding:12px;background:#151519;border-radius:12px;border:1px solid #F59E0B;margin-top:8px">
        <span class="pill pill-amber" style="margin-bottom:4px">INNINGS BREAK</span>
        <div style="font-size:18px;font-weight:800;color:#FFFFFF;margin:4px 0">Target: {inn1_total + 1} for India</div>
        <div class="score-label">Pakistan finished at {inn1_total}/{inn1_wkts} in 20 overs</div>
        <div style="font-size:11px;color:#E2E8F0;margin-top:4px">Innings 1 Top Moment: <b>{best_txt}</b></div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── G. Chat and Vibe (Chat Rewind) ────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
    <span class="section-label">💬 CHAT REWIND & VIBE METER</span>
</div>
''', unsafe_allow_html=True)

# Vibe data for current over
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

    # Semicircle mood gauge
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mood_val,
        title={'text': mood_label, 'font': {'size': 13, 'color': '#FFFFFF', 'family': 'Inter'}},
        number={'font': {'size': 26, 'color': '#FFFFFF', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': '#2A2A31'},
            'bar': {'color': '#D91E2B', 'thickness': 0.28},
            'bgcolor': '#2A2A31',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 33], 'color': '#14532D'},
                {'range': [33, 66], 'color': '#78350F'},
                {'range': [66, 100], 'color': '#7F1D1D'},
            ],
            'shape': 'angular',
        }
    ))
    gauge_fig.update_layout(
        height=150,
        margin=dict(l=15, r=15, t=25, b=5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(gauge_fig, use_container_width=True, config={'displayModeBar': False})

    # Theme chips
    theme_html = ''.join([f'<span class="pill pill-blue">{t}</span>' for t in themes[:3]])
    st.markdown(f'<div style="margin-bottom:8px;display:flex;gap:4px;flex-wrap:wrap">{theme_html}</div>', unsafe_allow_html=True)

    # Hottest take
    hottest_msg = next((m for m in chat_data if m["id"] == hottest_id), None)
    if hottest_msg:
        st.markdown(f'''
        <div class="card-gold">
            <div style="font-size:10px;color:#F5B301;font-weight:800;margin-bottom:2px">🔥 HOTTEST TAKE</div>
            <div class="chat-handle">{hottest_msg["handle"]}</div>
            <div class="chat-text">{hottest_msg["text"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    # Banter tone & Banter Guard Abuse Blocked counter
    st.markdown(f'''
    <div style="display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap;align-items:center">
        <span class="pill pill-{"amber" if banter_tone == "Heated" else "green"}">{banter_tone} Tone</span>
        <span class="pill pill-muted">🛡 Abuse blocked: {abuse_count_total}</span>
    </div>
    ''', unsafe_allow_html=True)

# Latest 15 simulated messages up to current cursor
chat_up_to = [m for m in chat_data if m["ball_idx"] <= bidx]
latest_chat = chat_up_to[-15:] if chat_up_to else []

if not latest_chat:
    st.markdown('<div class="score-label" style="text-align:center;padding:12px">Chat will appear as deliveries are bowled...</div>', unsafe_allow_html=True)
else:
    for msg in latest_chat:
        is_abuse = msg.get("type") == "abuse"
        is_pinned = msg.get("is_pinned", False) or msg.get("type") == "shoutout"
        db = msg.get("dreambucks", 0)

        if is_abuse:
            # Abusive messages appear collapsed as Message hidden by Banter Guard with show toggle
            st.markdown(f'''
            <details class="abuse-guard">
                <summary>🛡 Message hidden by Banter Guard <span style="color:#60A5FA;font-size:10px;margin-left:4px">[Tap to Show]</span></summary>
                <div class="abuse-revealed">
                    <span class="chat-handle">{msg["handle"]}:</span> {msg["text"]}
                </div>
            </details>
            ''', unsafe_allow_html=True)
        elif is_pinned:
            st.markdown(f'''
            <div class="chat-msg-pinned">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
                    <span class="chat-handle">{msg["handle"]}</span>
                    {"<span class='dreambucks'>💰 " + str(db) + " DreamBucks</span>" if db > 0 else ""}
                </div>
                <div class="chat-text">{msg["text"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-msg">
                <span class="chat-handle">{msg["handle"]}:</span>
                <span class="chat-text"> {msg["text"]}</span>
            </div>
            ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── H. Footer ─────────────────────────────────────────────────
st.markdown('''
<div class="footer-text">
    Simulated chat for demonstration purposes.<br>
    Independent prototype inspired by public information about Dream11 Watch Along.<br>
    Not an official Dream11 product.
</div>
''', unsafe_allow_html=True)

with st.expander("ℹ️ How Watch-Along Copilot works"):
    st.markdown("""
    **Core System Principles:**
    1. **100% Deterministic Base**: Every probability, alert trigger, and score derives from pure Python rules (no AI hallucinated stats).
    2. **Chase Meter**: Modeled using a calibrated logistic pressure function:
       $$\\text{pressure} = \\text{RRR} - \\text{Par}(\\text{wickets in hand})$$
       $$\\text{Chase} = \\frac{1}{1 + e^{0.45 \\times \\text{pressure}}}$$
    3. **Tension Formula per Ball**:
       $$\\text{raw} = 0.9 \\times \\text{swing} + \\text{event\\_pts} \\times \\text{phase\\_mult} + \\text{closeness}$$
       $$\\text{tension} = \\text{clamp}\\left(100 \\times \\frac{\\text{raw}}{\\text{P95}}, 0, 100\\right) + \\text{star\\_bonus}$$
    4. **Smart Alerts**: Filter deliveries using sensitivity thresholds (Calm=75, Normal=60, Hyped=45) with minimum pacing intervals.
    5. **AI Synthesis**: Claude summarizes watch-along chat vibe and builds 20-second catch-ups, strictly constrained to facts passed by code.
    """)


# ── Auto-play logic ───────────────────────────────────────────
if st.session_state.playing and st.session_state.ball_idx < len(balls) - 1:
    speed_delay = config.PLAY_SPEED.get(st.session_state.speed, 1.0)
    time.sleep(speed_delay)
    st.session_state.ball_idx += 1
    st.rerun()
elif st.session_state.playing and st.session_state.ball_idx >= len(balls) - 1:
    st.session_state.playing = False
