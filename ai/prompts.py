"""Prompt templates used verbatim as specified."""

CHAT_PROMPT = """You write realistic simulated live chat for a cricket watch-along app used by Indian fans. Input is match facts for overs {start_over} to {end_over} as JSON. Return ONLY a JSON array of objects with keys over, text, lang, type, handle, team_side. Rules: about 60 percent Hinglish in Roman script; each text under 120 characters; reactions must fit the events (wicket means shock or joy, six means hype); handles are fictional; follow this type mix: hype 30, banter 20, analysis 15, question 10, roast 10, shoutout 8, abuse 5, neutral 2; abuse must be mild generic rudeness with no slurs and no targeting of any group; never state a score or number that is not in the facts."""

VIBE_PROMPT = """You read live chat from a cricket watch-along. Using ONLY the messages and events given, return JSON with themes, mood, mood_label, hottest_take, funniest, banter_tone, summary_line as specified. Themes must be paraphrases of what the messages actually talk about."""

WALKIN_PROMPT = """You are a friendly cricket watch-along host. A fan just joined late. Using ONLY the facts below, write a 20-second catch-up. Return JSON with headline, story, what_matters_now, watch_this_player, room_mood, join_line. Language: {language}. Do not invent any number, player or event that is not in the facts."""

ALERT_PROMPT = """In at most 14 words, tell the fan why this moment matters, using only these facts. Language: {language}."""

