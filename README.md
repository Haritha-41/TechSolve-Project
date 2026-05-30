# SocialSense RAG

SocialSense RAG is a zero-cost full-stack starter for comparing any two supported social videos from YouTube or Instagram with transcript-grounded chat.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.11+
- RAG: LangChain
- LLM: Gemini free tier through Google Generative AI API
- Embeddings: local sentence-transformers by default
- Vector DB: local ChromaDB
- Transcript/media tools: youtube-transcript-api, yt-dlp, faster-whisper fallback

## Why Zero-Cost

The starter uses local embeddings and local ChromaDB storage. Gemini is configured for the free tier, and the media/transcript tools are open-source. No paid hosted database, queue, vector store, or inference endpoint is required.

## Setup

Install prerequisites:

- Node.js and npm
- Python 3.11+
- ffmpeg
- Git

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Required Environment Variables

Backend:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `CHROMA_PERSIST_DIR`
- `FRONTEND_ORIGIN`

Frontend:

- `NEXT_PUBLIC_API_URL`

## Architecture

The backend separates extraction, metadata calculation, transcript handling, chunking, embeddings, vector storage, memory, and RAG streaming. The default embedding provider is local sentence-transformers, with the provider isolated so Gemini embeddings can be added later. The frontend contains a URL form, side-by-side video cards, and a chat panel wired to backend APIs.

The MVP analyzes public YouTube and Instagram URLs with `yt-dlp`, computes engagement rate, stores transcript chunks in ChromaDB with source metadata, retrieves relevant chunks for each chat turn, and streams Gemini answers with requested citation formatting. You can compare two YouTube videos, two Instagram reels, or one of each. If `GEMINI_API_KEY` is missing, chat returns a configuration-safe retrieval response instead of failing silently.

## Scalability Notes

- Move ChromaDB to a managed or remote vector store if collections become large.
- Add background jobs for long media downloads and Whisper transcription.
- Cache transcript and metadata results by normalized URL.
- Replace in-memory chat memory with Redis or a database for multi-user sessions.
- Add provider adapters for additional LLMs and embedding models.

## Known Limitations

- Instagram transcription uses local Whisper fallback and can be slow on long videos.
- Some Instagram reels require session cookies. Set `INSTAGRAM_COOKIES_FILE` to a Netscape `cookies.txt` export when public extraction fails.
- Gemini answers require a free-tier `GEMINI_API_KEY`.
- Social platforms can rate-limit or block metadata extraction.
- Engagement metrics depend on what yt-dlp can access publicly.

## Demo Checklist

- Start backend and confirm `GET /health` returns `{"status":"ok"}`.
- Start frontend at `http://localhost:3000`.
- Enter any two supported YouTube or Instagram URLs.
- Confirm video cards show metadata and transcript preview.
- Ask a comparison question and confirm streamed answer output.
