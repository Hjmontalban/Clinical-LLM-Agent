# Clinical Evidence Assistant

**Evidence-Grounded Biomedical Research AI** — A full-stack platform that searches biomedical literature across multiple scholarly sources, performs hybrid retrieval and evidence extraction, synthesizes findings with claim-level citations, detects conflicting evidence, verifies citation support, and evaluates retrieval quality.

> **Disclaimer:** This is a research and evidence-synthesis tool, not a diagnostic system, prescribing system, or substitute for a licensed clinician.

## Features

- **Multi-source literature search** — PubMed, Semantic Scholar, and OpenAlex (concurrent)
- **Paper deduplication** — DOI, PMID, PMCID, and fuzzy title matching
- **Hybrid evidence ranking** — Semantic similarity + BM25 + study design + recency
- **PICO query planning** — LLM-powered query expansion
- **Evidence synthesis** — Executive summary, key findings, evidence tables
- **Conflict detection** — Identifies disagreements between studies
- **Citation verification** — Claim-level support classification
- **Safety gate** — Blocks diagnostic/prescription language
- **Mobile-first UI** — Responsive design with bottom navigation
- **Evaluation dashboard** — Real metrics from completed sessions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, TanStack Query, Recharts |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (dev) / PostgreSQL (production) |
| LLM | Groq (free — Llama 3.3 70B) or Google Gemini 2.0 Flash |
| Sources | PubMed E-utilities, Semantic Scholar, OpenAlex |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free tier recommended)

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — set GROQ_API_KEY and NCBI_EMAIL

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Recommended | Free LLM at [console.groq.com](https://console.groq.com) |
| `GEMINI_API_KEY` | Alternative | Google Gemini free tier |
| `LLM_PROVIDER` | No | `groq` (default) or `gemini` |
| `NCBI_EMAIL` | Yes | Your email for PubMed API |
| `DATABASE_URL` | No | Default: SQLite |
| `CORS_ORIGINS` | No | Default: localhost:3000 |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL (default: `http://localhost:8000`) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/search` | Quick literature search |
| POST | `/api/research` | Start full research pipeline |
| GET | `/api/research/{id}` | Get research status/results |
| GET | `/api/research/{id}/papers` | Get ranked papers |
| GET | `/api/research/{id}/verification` | Citation verification report |
| GET | `/api/evaluation` | Evaluation metrics |

## Deploy to Vercel

1. Push to GitHub
2. Import [Hjmontalban/Clinical-LLM-Agent](https://github.com/Hjmontalban/Clinical-LLM-Agent) in [Vercel](https://vercel.com)
3. **Critical settings** in Vercel → Project → Settings → General:
   - **Root Directory:** leave **empty** (repo root `.`) — do **not** set this to `frontend`
   - **Framework Preset:** Other (or leave as detected; `vercel.json` controls routing)
4. Set environment variables in Vercel dashboard:

| Variable | Required | Notes |
|----------|----------|-------|
| `GROQ_API_KEY` | Yes | Free key from [console.groq.com](https://console.groq.com) |
| `NCBI_EMAIL` | Yes | Your email for PubMed |
| `LLM_PROVIDER` | No | Default: `groq` |
| `CROSSREF_MAILTO` | No | Your email |
| `CORS_ORIGINS` | No | Set to your Vercel URL, e.g. `https://your-app.vercel.app` |

**Do not set** `NEXT_PUBLIC_API_URL` on Vercel — the frontend uses relative `/api` paths on the same domain.

5. Deploy

### Troubleshooting `NOT_FOUND` (404)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Vercel white page: `NOT_FOUND` | Root Directory set to `frontend` | Set Root Directory to **empty** (repo root) so `backend/` and root `vercel.json` are included |
| `DEPLOYMENT_NOT_FOUND` | Expired or failed deployment URL | Use your production URL (e.g. `https://clinical-llm-agent.vercel.app`) or redeploy from Vercel dashboard |
| `{"detail":"Not Found"}` on `/api` | Hitting `/api` without a route | Use `/api/health` instead |
| API works but research fails | Missing/invalid `GROQ_API_KEY` | Add a valid key in Vercel env vars |

**Verify deployment:** open `https://YOUR-APP.vercel.app/api/health` — you should see `{"status":"ok",...}`.

For production PostgreSQL, update `DATABASE_URL`:
```
postgresql+asyncpg://user:pass@host/dbname
```
(Add `asyncpg` to requirements.txt)

## Project Structure

```
├── frontend/          # Next.js application
│   ├── app/           # Pages (App Router)
│   ├── components/    # UI components
│   └── lib/           # API client, types
├── backend/
│   ├── app/
│   │   ├── api/       # FastAPI routes
│   │   ├── services/  # Search, AI, research pipeline
│   │   ├── models/    # Pydantic models
│   │   └── db/        # SQLAlchemy
│   └── api/           # Vercel serverless entry
└── vercel.json
```

## Safety

This application:
- Does NOT diagnose, prescribe, or provide emergency instructions
- Presents evidence with uncertainty communication
- Verifies citations against source abstracts
- Includes medical disclaimers on all reports
- Filters unsafe language (diagnosis, dosing directives)

## License

MIT
