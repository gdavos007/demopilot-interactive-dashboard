# DemoPilot

Interactive product demo agent for Carbon Black. Users ask questions via **chat** or **voice**, a RAG-backed knowledge agent answers from product documentation, and the UI navigates a **Storylane** dashboard to the relevant section.

## Architecture

```
Browser (localhost:3000)
  ├── Chat / Voice UI (Next.js + Material UI)
  ├── Storylane iframe navigation
  └── VAPI Web SDK (voice)

FastAPI Backend (localhost:8000)
  ├── Product Knowledge Agent (RAG + Claude Haiku 4.5)
  ├── VAPI webhook endpoints
  └── LangSmith evaluation framework (optional)
```

## Features

- **Interactive dashboard** — Storylane demo embedded in the UI with query-driven navigation
- **Chat interface** — RAG answers from scraped Carbon Black documentation
- **Voice interface** — VAPI-powered speech with dashboard navigation on transcript
- **LangSmith observability** — Tracing and LLM-as-judge evaluation (optional)
- **Async FastAPI backend** — REST API with OpenAPI docs

## Prerequisites

- Python 3.10+
- Node.js 18+
- API keys: Anthropic, VAPI (public + private), optional OpenAI and LangSmith

## Setup

### 1. Backend

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pip install "langchain>=0.3,<1.0" langchain-community langchain-huggingface langchain-core faiss-cpu
```

Create `.env` in the **project root**:

```env
VAPI_API_KEY=your_vapi_private_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
ANTHROPIC_API_KEY=your_anthropic_api_key
STORYLANE_SHARE_ID=zjalh0zmyhdm
OPENAI_API_KEY=your_openai_api_key          # optional, improves embeddings
LANGSMITH_TRACING=false                     # optional
LANGSMITH_API_KEY=your_langsmith_key        # optional
```

> **Note:** Backend `.env` is for server-side keys only. Do not put `NEXT_PUBLIC_*` variables here.

### 2. Frontend

```bash
cd frontend
npm install --legacy-peer-deps
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_VAPI_PUBLIC_KEY=your_vapi_public_key
NEXT_PUBLIC_VAPI_ASSISTANT_ID=your_vapi_assistant_id
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000   # optional
```

## Running the app

Use **two terminals**.

**Terminal 1 — Backend** (project root):

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Wait for the knowledge agent to finish scraping documentation on first startup (1–3 minutes).

**Terminal 2 — Frontend**:

```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

### Quick checks

| URL | Expected |
|-----|----------|
| http://localhost:3000 | DemoPilot UI with Storylane dashboard |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/api/v1/knowledge/status | Agent initialization status |

## Demo flow

1. **Interactive Dashboard** tab — Storylane demo loads in the iframe
2. Click **Test: API Access** or ask via voice: *"api access for custom integrations"*
3. **Chat Interface** tab — ask product questions, e.g. *"What platforms are supported?"*
4. Mic button (bottom-right) — start a VAPI voice session

## API endpoints

### Knowledge
- `POST /api/v1/knowledge/query` — Query the product knowledge agent
- `GET /api/v1/knowledge/status` — Agent and vector store status
- `GET /api/v1/knowledge/context/{query}` — Retrieve relevant context without generating a response

### Voice
- `POST /api/v1/voice/webhook` — Handle VAPI voice events
- `POST /api/v1/voice/speak` — Text-to-speech

### Evaluation (requires LangSmith)
- `GET /api/v1/evaluation/status` — Evaluation system status
- `POST /api/v1/evaluation/run-quick` — Run evaluation on 5 examples

See [LANGSMITH_EVALUATION_GUIDE.md](./LANGSMITH_EVALUATION_GUIDE.md) for evaluation setup.

## Project structure

```
app/                          # FastAPI backend
  api/v1/                     # REST routes (knowledge, voice, evaluation)
  core/
    knowledge/                # RAG agent (FAISS + Anthropic)
    voice/                    # VAPI client
    evaluation/               # LangSmith evaluators
  config/                     # Settings and logging
  models/                     # Pydantic schemas

frontend/                     # Next.js 15 UI
  app/
    components/               # Chat, DemoViewer, VoiceWidget
    lib/                      # Storylane controller, mapper, config

docs/
  PRD.md                      # Product requirements document
```

## Storylane navigation

Dashboard section URLs are mapped in `frontend/app/lib/storylaneMapper.ts`. The share ID is configured in `frontend/app/lib/storylaneConfig.ts` and `STORYLANE_SHARE_ID` in `.env`.

To update navigation targets, edit the `URLS` object in `storylaneMapper.ts` with page IDs from your Storylane share links.

## Testing

```bash
pytest
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: langchain.text_splitter` | Install pinned langchain: `pip install "langchain>=0.3,<1.0" langchain-community faiss-cpu` |
| `LangChainStringEvaluator` import error | Fixed in evaluators — restart backend |
| `NEXT_PUBLIC_VAPI_PUBLIC_KEY` validation error | Move frontend keys to `frontend/.env.local`, not root `.env` |
| Dashboard shows "Loading..." forever | Hard-refresh browser; ensure frontend is on latest code |
| Chat tab is blank | Hard-refresh; input is at bottom of the panel |
| Voice won't start | Verify `NEXT_PUBLIC_VAPI_PUBLIC_KEY` and `NEXT_PUBLIC_VAPI_ASSISTANT_ID` in `frontend/.env.local`, restart `npm run dev` |
| `npm run dev` ENOENT | Run from `frontend/` directory, not project root |

## Documentation

- [Product Requirements (PRD)](./docs/PRD.md)
- [LangSmith Evaluation Guide](./LANGSMITH_EVALUATION_GUIDE.md)

## License

MIT
