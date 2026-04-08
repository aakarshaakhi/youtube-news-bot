"""
render_video.py
---------------
Creates a professional news video using MoviePy + FFmpeg:
- Dark news-style background
- Animated text cards per story
- Voiceover audio layered in
- Outputs: output/final_video.mp4
"""

import json
import textwrap
from pathlib import Path
from moviepy.editor import (
    AudioFileClip, ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ImageClip
)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Video settings
WIDTH, HEIGHT = 1280, 720   # 720p HD (YouTube standard)
FPS = 24
BG_COLOR = (10, 10, 20)     # Deep navy black
ACCENT_COLOR = (220, 50, 50) # News red
TEXT_COLOR = (240, 240, 240)
CAT_COLOR = (100, 180, 255)

SEGMENT_DURATION = 24  # seconds per story card (~5 stories = ~2 min)
INTRO_DURATION = 6
OUTRO_DURATION = 8


def make_frame_array(width, height, bg_color, texts):
    """
    Create a single numpy frame (image) with styled text layout.
    texts = list of (text, font_size, color, y_position, bold)
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw red top bar
    draw.rectangle([(0, 0), (width, 8)], fill=ACCENT_COLOR)
    # Draw red bottom bar
    draw.rectangle([(0, height - 8), (width, height)], fill=ACCENT_COLOR)
    # Subtle vertical left accent
    draw.rectangle([(0, 0), (6, height)], fill=ACCENT_COLOR)

    for (text, font_size, color, y_pos, align) in texts:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Word wrap
        wrapped = textwrap.fill(text, width=52)
        lines = wrapped.split("\n")

        line_height = font_size + 6
        total_h = line_height * len(lines)
        cur_y = y_pos

        for line in lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = len(line) * (font_size // 2)

            if align == "center":
                x = (width - tw) // 2
            else:
                x = 60  # left aligned with margin

            draw.text((x, cur_y), line, font=font, fill=color)
            cur_y += line_height

    return np.array(img)


def make_clip(frame_array, duration):
    """Convert numpy frame to a MoviePy ImageClip."""
    return ImageClip(frame_array).set_duration(duration)


def make_intro_clip(data):
    texts = [
        ("📺  DAILY NEWS DIGEST", 28, ACCENT_COLOR, 60, "center"),
        ("", 20, TEXT_COLOR, 110, "center"),
        (data["intro_script"], 26, TEXT_COLOR, 160, "center"),
    ]
    frame = make_frame_array(WIDTH, HEIGHT, BG_COLOR, texts)
    return make_clip(frame, INTRO_DURATION)


def make_story_clip(story, index):
    headline_wrapped = textwrap.fill(story["headline"], 42)
    script_preview = story["script"][:220] + "..."

    texts = [
        (f"STORY {index}  •  {story['category'].upper()}", 22, CAT_COLOR, 50, "left"),
        (headline_wrapped, 34, TEXT_COLOR, 110, "left"),
        (script_preview, 20, (190, 190, 190), 320, "left"),
    ]
    frame = make_frame_array(WIDTH, HEIGHT, BG_COLOR, texts)
    return make_clip(frame, SEGMENT_DURATION)


def make_outro_clip(data):
    texts = [
        ("👍  LIKE  •  SUBSCRIBE  •  🔔 BELL", 30, ACCENT_COLOR, 200, "center"),
        (data["outro_script"], 24, TEXT_COLOR, 310, "center"),
        ("Daily News Digest", 22, CAT_COLOR, 520, "center"),
    ]
    frame = make_frame_array(WIDTH, HEIGHT, BG_COLOR, texts)
    return make_clip(frame, OUTRO_DURATION)


def render_video():
    print("[render_video] Loading script data...")
    with open(OUTPUT_DIR / "script_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("[render_video] Building video clips...")
    clips = []
    clips.append(make_intro_clip(data))
    for i, story in enumerate(data["stories"], 1):
        clips.append(make_story_clip(story, i))
    clips.append(make_outro_clip(data))

    print("[render_video] Concatenating clips...")
    video = concatenate_videoclips(clips, method="compose")

    print("[render_video] Loading voiceover audio...")
    audio = AudioFileClip(str(OUTPUT_DIR / "voiceover.mp3"))

    # Trim audio or video to match shorter one
    min_dur = min(video.duration, audio.duration)
    video = video.subclip(0, min_dur)
    audio = audio.subclip(0, min_dur)

    final = video.set_audio(audio)

    out_path = str(OUTPUT_DIR / "final_video.mp4")
    print(f"[render_video] Rendering MP4 → {out_path}")
    final.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )
    print(f"[render_video] ✅ Video ready → {out_path}")


if __name__ == "__main__":
    render_video()
