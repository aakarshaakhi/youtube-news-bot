"""
fetch_news.py
-------------
Calls Claude API to fetch today's top news and generate:
- Full video script
- YouTube title
- Description
- Hashtags
- Chapter timestamps
Saves output to output/script_data.json
"""

import os
import json
import datetime
from pathlib import Path
import anthropic

# ── Setup ──────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TODAY = datetime.date.today().strftime("%B %d, %Y")

SYSTEM_PROMPT = """You are a professional YouTube news script writer.
Your job is to write engaging, clear, and original daily news scripts for a YouTube channel.
Always respond ONLY in valid JSON. No markdown, no explanation outside JSON."""

USER_PROMPT = f"""Today is {TODAY}.

Search the web and find the top 5 most important global news stories today.
For each story write a 60-second narration segment (about 150 words).

Return ONLY this JSON structure:
{{
  "youtube_title": "Top 5 News Today - {TODAY} | Daily News Digest",
  "description": "A 3-paragraph YouTube description summarizing today's episode. End with a call to subscribe.",
  "hashtags": ["#DailyNews", "#NewsToday", "#BreakingNews", "#WorldNews", "#TopStories"],
  "stories": [
    {{
      "headline": "Story headline here",
      "category": "Politics / Tech / Business / Science / World",
      "script": "Full 150-word narration for this story...",
      "timestamp": "0:00"
    }}
  ],
  "intro_script": "Welcome to Daily News Digest! I'm your AI anchor. Here are today's top 5 stories for {TODAY}.",
  "outro_script": "That's all for today's Daily News Digest. If you found this helpful, please like, subscribe, and hit the bell icon so you never miss an update. See you tomorrow!"
}}

Make timestamps sequential: story 1 at 0:30, story 2 at 2:30, story 3 at 4:30, story 4 at 6:30, story 5 at 8:30."""

# ── API Call ───────────────────────────────────────────────────────────────────
def fetch_news_script():
    print(f"[fetch_news] Fetching top news for {TODAY}...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}]
    )

    # Extract text content from response (skip tool_use blocks)
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    # Clean and parse JSON
    clean = full_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip().rstrip("```").strip()

    data = json.loads(clean)

    # Save to file
    out_path = OUTPUT_DIR / "script_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[fetch_news] ✅ Script saved → {out_path}")
    print(f"[fetch_news] Title: {data['youtube_title']}")
    return data


if __name__ == "__main__":
    fetch_news_script()
