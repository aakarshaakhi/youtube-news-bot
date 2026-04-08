"""
generate_voice.py
-----------------
Converts the news script to MP3 voiceover using gTTS (Google Text-to-Speech).
gTTS is completely free — no API key needed.
Saves: output/voiceover.mp3
"""

import json
from pathlib import Path
from gtts import gTTS

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def build_full_script(data: dict) -> str:
    """Combine intro + all stories + outro into one narration."""
    parts = []

    parts.append(data["intro_script"])
    parts.append("")  # pause

    for i, story in enumerate(data["stories"], 1):
        parts.append(f"Story {i}. {story['headline']}.")
        parts.append("")
        parts.append(story["script"])
        parts.append("")  # breath pause between stories

    parts.append(data["outro_script"])

    return "\n".join(parts)


def generate_voice():
    # Load script
    script_path = OUTPUT_DIR / "script_data.json"
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    full_script = build_full_script(data)

    print(f"[generate_voice] Script length: {len(full_script)} characters")
    print("[generate_voice] Generating voiceover with gTTS...")

    # gTTS — free, no key needed, uses Google's TTS engine
    tts = gTTS(text=full_script, lang="en", slow=False)

    out_path = OUTPUT_DIR / "voiceover.mp3"
    tts.save(str(out_path))

    print(f"[generate_voice] ✅ Voiceover saved → {out_path}")


if __name__ == "__main__":
    generate_voice()
