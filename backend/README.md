# Backend

FastAPI starter for TechSolve Test.

## Setup

Requires Python 3.11+ and ffmpeg.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## Instagram Cookies

Some public Instagram Reels expose more metadata when `yt-dlp` has a logged-in browser cookie export.
Export cookies in Netscape `cookies.txt` format, save them outside git, and point the backend to the file:

```env
INSTAGRAM_COOKIES_FILE=./data/instagram-cookies.txt
```

Quick metadata probe without running the full RAG flow:

```bash
python scripts/probe_instagram_metadata.py \
  "https://www.instagram.com/reel/SHORTCODE/"
```

## Apify Instagram Fallback

If public Reel views are missing from `yt-dlp`, the backend can optionally call an Apify Reel scraper.
Keep the token in `backend/.env` only:

```env
INSTAGRAM_VIEW_PROVIDER=apify
APIFY_TOKEN=your_apify_token
APIFY_REEL_ACTOR_ID=pratikdani/instagram-reels-scraper
APIFY_TIMEOUT_SECONDS=180
```

For `apidojo/instagram-scraper-api`, the backend sends a single Reel URL in `startUrls` with `maxItems=1` and reads nested `video.playcount` as the view count.
For `pratikdani/instagram-reels-scraper`, the backend sends the single Reel URL as `url` with `use_cache=false`.
