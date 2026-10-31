# 🏏 Watch-Along Copilot

> **Dream11 FDE Assignment — October 2026**  
> An AI second-screen companion for creator-led sports watch-alongs. Replaying India vs Pakistan (T20 World Cup 2022 at the MCG).

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit 1.40](https://img.shields.io/badge/streamlit-1.40.0-FF4B4B.svg)](https://streamlit.io/)
[![Tests passing](https://img.shields.io/badge/tests-44%20passed-22C55E.svg)]()
[![Zero API Key Required](https://img.shields.io/badge/runtime-0%20API%20key%20required-F5B301.svg)]()

---

## 1. Mission & The Fan Problem

Dream11 has evolved into a free-to-play, second-screen sports entertainment ecosystem. The core experience is **creator-led watch-alongs** where fans chat, send Shout Outs and gifts, spend DreamBucks, and follow stats alongside the stream.

However, Dream11 faces three critical fan adoption barriers:
1. **The Late-Joiner Drop-off**: Fans hopping in mid-innings feel disoriented by scores without narrative context and bounce within 30 seconds.
2. **Chat Clutter & Toxicity**: High-velocity live chat moves too fast to parse, while brand-sensitive advertisers require clean, brand-safe environments.
3. **The Attention Dilemma**: Casual fans cannot watch 4 hours uninterrupted; they miss pivotal moments while cooking, working, or scrolling.

**Watch-Along Copilot** solves all three on a single phone-shaped screen:
- **Walk-In Ready**: A 20-second punchy catch-up briefing generated for any ball of the match in English or Hinglish.
- **Chat Rewind & Vibe Meter**: Live room mood gauge, theme summaries, hottest takes, and Banter Guard abuse shielding.
- **Wake Me When It Matters**: Real-time mathematical tension scoring per delivery, notifying fans exactly when tension surges with a 1-tap **Join Live** bridge.

---

## 2. The Three Core Features

### 🚶 Feature 1: Walk-In Ready (20s Catch-Up)
- One tap on **"🔴 Walk me in"** opens an instant briefing modal or inline card.
- Summarizes match situation, the exact 2-line story, what matters now, key player to watch, and current watch-along room mood.
- Instant switch between **English** and natural **Hinglish** (Roman script).
- **Strictly Grounded**: Every number is verified by code validation against match facts—zero AI hallucination.

### 💬 Feature 2: Chat Rewind & Vibe Meter
- Semicircle visual mood gauge (0–100) classifying crowd sentiment: *Nervous, Hyped, Heartbreak, Chilling, Roasting, Electric*.
- Top 3 conversational themes updated dynamically as the game unfolds.
- **🔥 Hottest Take** card with gold border and DreamBucks recognition.
- **🛡 Banter Guard**: Live abuse mitigation counter. Toxic/abusive messages are collapsed by default with an optional fan reveal toggle.

### ⚡ Feature 3: Wake Me When It Matters
- Area tension curve rendered **strictly up to the current delivery** so the replay feels genuinely live.
- Top 5 match landmarks pinned as diamond markers (1 to 5) spaced at least 12 balls apart.
- Configurable fan preferences: **Favourite Team**, **Favourite Star Player** (+3 tension boost on their balls), and **Alert Sensitivity** (*Calm 75, Normal 60, Hyped 45*).
- Mock mobile notification alerts with trigger diagnosis (*Wicket, Six, Four, Swing, Close finish*), why-now lines, and **Join Live** toast trigger.
- Live telemetry: "Alerts sent" count and "% balls safely skippable".

---

## 3. Mathematical Tension Engine & Chase Meter

All analytics and numbers are 100% deterministic pure Python logic without model dependency.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CHASE METER (Innings 2 Win Probability)                  │
│    rrr      = runs_needed * 6 / balls_left                  │
│    par      = 9.0 * (0.45 + 0.55 * (wkts_in_hand / 10)^0.6) │
│    pressure = rrr - par                                     │
│    chase    = 1 / (1 + exp(0.45 * pressure))                │
│    Clamped to [0.02, 0.98]; 1.0 on win, 0.0 on all-out/loss │
├─────────────────────────────────────────────────────────────┤
│ 2. PROJECTED SCORE (Innings 1)                              │
│    crr_ball = cum_runs / legal_balls_bowled                 │
│    proj     = cum_runs + balls_left * (0.6*crr + 0.4*8.5/6) │
├─────────────────────────────────────────────────────────────┤
│ 3. TENSION SCORE PER BALL                                   │
│    swing      = |chase_after - chase_before| * 100          │
│    event_pts  = Wicket: 6 | Six: 4 | Four: 2                │
│                 Dot: 0.5  | Extras: 1 | Other: 1            │
│    phase_mult = Powerplay (0-5ov): 1.2                      │
│                 Middle (6-14ov):   1.0                      │
│                 Death (15-19ov):   1.4                      │
│    closeness  = (1 - |chase_after - 0.5| * 2) * 8.0         │
│    raw        = 0.9*swing + event_pts*phase_mult + closeness│
│    tension    = clamp(100 * raw / P95(raw), 0, 100)         │
│                 + star_player_bonus (+3)                    │
│    smoothed   = 3-ball rolling mean (chart display only)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Architecture Diagram

```
                 CRICSHEET OFFICIAL MATCH JSON
                  (MCG 2022: IND vs PAK T20)
                              │
                              ▼
                   logic/parse.py (Pure Python)
                              │
                              ▼
                      data/balls.csv
            (251 deliveries, ball-by-ball facts)
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
   DETERMINISTIC LOGIC                     OFFLINE PRECOMPUTE
  - logic/chase.py                        - precompute/gen_chat.py
  - logic/tension.py                      - precompute/gen_vibe.py
  - logic/alerts.py                       - precompute/gen_walkin.py
  - logic/state.py                        - precompute/gen_alerts.py
         │                                         │
         │                              (Claude LLM / Fallbacks)
         │                                         │
         │                                         ▼
         │                                COMMITTED CACHES
         │                                - data/chat.json (450 msgs)
         │                                - cache/vibe.json (40 overs)
         │                                - cache/walkin.json (80 cards)
         │                                - cache/alerts.json (66 lines)
         │                                         │
         └────────────────────┬────────────────────┘
                              │
                              ▼
                     STREAMLIT UI (app.py)
          - Max 430px mobile-first phone chassis
          - Real-time Match Clock slider + 1x/2x/5x autoplay
          - Plotly tension curve + 5 pinned moments
          - Smart alert feed with Join Live toasts
          - Walk-In Ready modal dialog (English/Hinglish)
          - Semicircle mood gauge + Banter Guard filter
```

---

## 5. What Is Real vs. What Is Simulated

| Component | Status | Source / Grounding |
|---|---|---|
| **Match Scores & Deliveries** | **REAL** | Official Cricsheet ball-by-ball JSON (IND vs PAK, T20 WC 2022, 160/6 vs 159/8). |
| **Run Rates & Target Math** | **REAL** | Pure mathematical calculations derived delivery by delivery. |
| **Chase Meter & Par Scores** | **REAL MODEL** | Deterministic logistic pressure formula calibrated to T20 MCG chase dynamics. |
| **Tension Scores & Top 5 Moments** | **REAL MODEL** | Pure Python formula combining swing, event weight, death multipliers, and P95 scaling. |
| **Watch-Along Chat** | **SIMULATED** | 450 simulated fan messages generated offline with strict 70-handle distribution and Hinglish mix. |
| **Vibe Meter & Themes** | **SIMULATED** | Windowed NLP aggregation of simulated chat per over. |
| **Banter Guard Abuse Blocker** | **SIMULATED** | Fictional mild rudeness quarantined and counted via code classification. |
| **DreamBucks & Shout Outs** | **SIMULATED** | Mock gamification overlay matching Dream11 Watch-Along vocabulary. |

---

## 6. How to Run Locally in 3 Commands

Clone the repository and run:

```bash
# 1. Navigate to directory
cd "Dream11 Wake Me Up"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application (no API keys or setup required!)
streamlit run app.py
```

Open `http://localhost:8501` in your browser.  
*(Optional: Open Chrome DevTools and switch device simulation to iPhone 12/13/14 Pro - 390px width).*

---

## 7. How to Regenerate Caches (Optional, requires Claude API Key)

The repository comes pre-bundled with all verified data and caches. If you wish to regenerate fresh AI narratives with Anthropic Claude:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Put your key in `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   CLAUDE_MODEL=claude-sonnet-4-20250514
   ```
3. Run the master precompute script:
   ```bash
   python precompute/build_all.py
   ```
4. Run validation test suite:
   ```bash
   pytest tests/ -v
   ```

---

## 8. AI Tools & Models Used

- **Claude 3.5 Sonnet / Claude Models (`anthropic` SDK)**: Used in precompute scripts for high-empathy Hinglish chat simulation, conversational vibe extraction, and 20-second Walk-In catch-ups with rigid fact grounding.
- **Antigravity Coding Agent**: Autonomous full-stack pair programming, architecture design, test harness authoring, and mobile UI implementation.
- **Cricsheet Data**: Verified open cricket ball-by-ball archive.
- **Streamlit & Plotly**: Dark-mode phone interface, custom CSS styling, and live-updating SVG area charts.

---

## 9. Limitations & Out of Scope

- **Rain Interruptions / DLS**: Standard 20-over uninterrupted matches assumed (DLS table calculation out of scope).
- **Super Overs**: Single match resolution terminates at target reached or 20 overs completed.
- **Live WebSocket Chat**: Real-time multi-user WebSocket ingestion is simulated through cursor-synced data stores.

---

## 10. Future Roadmap

1. **Creator Cue Cards**: Giving watch-along hosts real-time talking points ("80% of fans are roasting the fielding setup").
2. **Audio Walk-In Ready**: 15-second natural speech briefing synthesized via ElevenLabs for eyes-free catch-up.
3. **Multi-Regional Languages**: Expanding beyond English and Hinglish to Tamil, Telugu, Bengali, and Marathi sports fan dialects.
4. **Advertiser Brand Safety Telemetry**: Live sentiment indexing giving brand sponsors real-time guarantee of safe placement during watch-along peaks.

---

## 11. Draft 200-Word Note (Section 14)

> As Dream11 expands into creator-led watch-alongs, its core challenge is adoption: getting fantasy users to tune into streams, stay engaged, and feel part of the community without getting overwhelmed by noisy chat or losing context when joining late.
> 
> Watch-Along Copilot solves this with three connected features. **Walk-In Ready** provides a 20-second narrative catch-up card in English or Hinglish so fans immediately understand the match state and room energy. **Chat Rewind & Vibe Meter** parses simulated watch-along chat into an instant mood gauge with Banter Guard filtering mild toxicity for brand safety. **Wake Me When It Matters** runs a deterministic mathematical tension engine per delivery, alerting fans during critical swings so they can jump straight into the action with one tap.
> 
> All stats, win probabilities, and tension scores are calculated in pure Python using official Cricsheet ball data—AI never invents facts. Claude was used during precomputation to synthesize chat sentiment and generate natural catch-ups grounded strictly in match events, allowing the full dashboard to run with zero API keys or external latency.

*(Word count: 172 words — strictly under the 190-word threshold).*

---

## 12. 90-Second Demo Script (Section 15)

- **00:00 – 00:10 | The Problem Hook**  
  *"Dream11 is transforming into a second-screen watch-along hub. But fans joining late feel lost, live chat is noisy, and busy users miss critical turning points. Here is Watch-Along Copilot."*

- **00:10 – 00:35 | Wake Me When It Matters**  
  *"First, look at the tension curve for India vs Pakistan. During quiet middle overs, tension sits low and alerts stay quiet—saving fans from notification fatigue. Now watch as I drag the match clock to the 19th over. Tension spikes above 90! A mock phone notification fires with an exact why-now line. I tap 'Join Live' and get bridged straight into the stream with zero friction."*

- **00:35 – 01:00 | Walk-In Ready (Catch-Up Card)**  
  *"What if you just opened the app right now? Tap 'Walk me in'. In 20 seconds, you get the headline, the 2-sentence story, what matters now, who to watch, and room mood. Toggle to Hinglish—instantly localized into natural fan vernacular. Every single number is 100% grounded in code facts."*

- **01:00 – 01:20 | Chat Rewind & Vibe Meter**  
  *"Below the scoreboard, Chat Rewind gives creators and fans an instant read of the room. The semicircle gauge shows crowd sentiment, theme chips summarize topics, and the Hottest Take highlights top fan shoutouts. Meanwhile, Banter Guard quarantines abusive messages with an expandable reveal, keeping streams brand-safe."*

- **01:20 – 01:30 | Value & Close**  
  *"Watch-Along Copilot turns passive score-checkers into active watch-along participants—driving adoption for Dream11, engagement for creators, and brand safety for sponsors."*

---

## 13. Verification & Acceptance Checklist

- [x] **M1 Data**: Official IND vs PAK T20 WC 2022 parsed into `data/balls.csv` (251 balls). Totals verify 159/8 and 160/6.
- [x] **M2 Logic**: Chase meter, tension formula, alerts, key moments, state_at all pass 38 unit tests.
- [x] **M3 Chat**: 450 simulated chat messages distributed by tension, ~60% Hinglish, valid schemas.
- [x] **M4 Caches**: 40 vibe entries, 80 walk-in entries, 66 alert entries passing number validation.
- [x] **M5-M8 UI**: Max 430px dark mobile theme, Plotly tension chart, mood gauge, smart alerts, modal catch-up card, Banter Guard.
- [x] **M9 Quality**: 390px mobile viewport certified, WCAG AA contrast, edge cases (Ball 0, Innings break) fully handled.
- [x] **M10 Testing**: 44 pytest unit tests passing. Zero API key runtime.

---

## 14. License & Disclaimers

Independent prototype inspired by public information about Dream11 Watch Along.  
Not an official Dream11 product.  
Chat and user handles are simulated.
