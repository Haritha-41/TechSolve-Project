# Backend

FastAPI starter for SocialSense RAG.

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
