# 📺 YouTube Daily News Bot

Fully automated YouTube news channel pipeline.
Runs daily via GitHub Actions — zero effort after setup.

## 🗺️ Pipeline
```
GitHub Actions (cron: daily 7:30 AM IST)
  → fetch_news.py      (Claude API — news + script)
  → generate_voice.py  (gTTS — free voiceover)
  → render_video.py    (MoviePy — MP4 video)
  → upload_youtube.py  (YouTube Data API — auto upload)
```

## ⚙️ GitHub Secrets Required
| Secret Name | Where to get it |
|-------------|----------------|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `YOUTUBE_CLIENT_ID` | Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | Run get_youtube_token.py once |

## ▶️ Start / Pause / Stop
| Action | How |
|--------|-----|
| Start | Push this repo — cron auto-activates |
| Manual run | GitHub app → Actions → Run workflow |
| Pause | GitHub app → Actions → Disable workflow |
| Resume | GitHub app → Actions → Enable workflow |
| Stop forever | Delete daily_news.yml |

## 📊 Monitor
GitHub app → Actions tab → green ✅ = success, red ❌ = check logs
