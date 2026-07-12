# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

DemoPilot is an agentic product-demo app for **CrowdStrike Falcon**. A user asks a question (chat or voice); a RAG knowledge agent answers from ingested product docs, and the UI drives an embedded **Storylane** demo iframe to the relevant dashboard section. The agent loop is **perceive → retrieve → reason → act**.

It's a two-process app: a **FastAPI backend** (`app/`, port 8000) and a **Next.js 15 frontend** (`frontend/`, port 3000). They run in separate terminals.

## Commands

### Backend (run from project root)
```bash
source venv/bin/activate            # or .venv — two virtualenvs exist in the repo
uvicorn app.main:app --reload       # serves on :8000; Swagger at /docs
pytest                              # all tests
pytest tests/test_knowledge_agent.py::test_fallback_product_info   # single test (tests are function-based)
black . && isort .                  # format (line-length 88, black profile)
mypy app                            # type-check
python run_evaluation.py            # LangSmith LLM-as-judge eval (needs LangSmith keys)
```

First backend startup scrapes documentation and builds the FAISS index — expect **1–3 min** before `/api/v1/knowledge/status` reports `vector_store_initialized: true`.

Dependencies: the project uses `pyproject.toml` + `uv.lock`, but the documented install path is pip: `pip install -e ".[dev]"`. LangChain **must** be pinned `>=0.3,<1.0` — v1 breaks the current langchain ecosystem pins and import layout this code relies on.

### Frontend (run from `frontend/`)
```bash
npm install --legacy-peer-deps      # React 19 vs MUI peer-dep conflict requires this flag
npm run dev                         # :3000
npm run build
npm run lint
```

## Configuration (two separate env files — do not mix)

- **Backend `.env`** (project root): `ANTHROPIC_API_KEY`, `VAPI_API_KEY`, `VAPI_ASSISTANT_ID`, `STORYLANE_SHARE_ID` are **required at import time** (see below). Optional: `OPENAI_API_KEY`, `PRODUCT_TYPE` (`crowdstrike`|`carbon_black`|`prisma_cloud`, default `crowdstrike`), `LANGSMITH_*`. Settings use `extra="ignore"`, so stray vars won't crash it, but the required ones with no default will.
- **Frontend `frontend/.env.local`**: `NEXT_PUBLIC_VAPI_PUBLIC_KEY`, `NEXT_PUBLIC_VAPI_ASSISTANT_ID` (required), `NEXT_PUBLIC_BACKEND_API_URL` (optional, defaults to `http://localhost:8000`). Don't put `NEXT_PUBLIC_*` in the backend `.env` — they're frontend-only. Backend settings use `extra="ignore"`, so extras won't crash it, but mixing the two files causes confusion.

## Architecture

### Backend — the knowledge agent is the core
`app/core/knowledge/agent.py` defines `ProductKnowledgeAgent` and a **module-level singleton** `knowledge_agent` created at import. Because the singleton constructs on import, the required env vars must exist whenever any module imports the agent (including tests). `app/main.py`'s FastAPI `lifespan` calls `knowledge_agent.initialize_agent()` on startup.

Pipeline per query (`get_response`):
1. **Retrieve** — `query_knowledge_base` runs FAISS similarity search (top-k=4) over doc chunks (1000 chars, 200 overlap).
2. **Reason** — `_generate_llm_response` builds a system prompt with retrieved context and calls the LLM. Generation model is **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`), hardcoded in two places in this file (raw Anthropic client + LangChain `ChatAnthropic`).
3. Returns `KnowledgeResponse` (response text, context docs, confidence 0.8 if context found else 0.5).

**LLM path selection matters when editing generation:**
- If LangSmith is enabled → LangChain `ChatAnthropic` (traced) is tried first.
- Otherwise → the raw `anthropic` client.
- On any Anthropic failure → OpenAI `gpt-4o-mini` fallback, but only if `OPENAI_API_KEY` is set.
- Embeddings mirror this: OpenAI embeddings if `OPENAI_API_KEY` present, else HuggingFace `all-MiniLM-L6-v2` (local, no key).

**Ingestion / knowledge sources:** For `crowdstrike`, docs are a fixed Q&A set of Dropbox-hosted HTML pages defined in `app/config/knowledge_docs.py` (`CROWDSTRIKE_KNOWLEDGE_DOCS`). `dropbox_direct_url()` rewrites `dl=0`→`dl=1` so Dropbox serves raw HTML; `html_extractor.py` strips it to text. If a scrape fails, `CROWDSTRIKE_FALLBACK_ANSWERS` (currently empty) or `_add_fallback_product_info()` provides hardcoded text so the agent still answers. The `carbon_black` and `prisma_cloud` branches scrape live vendor URLs instead.

API routes live in `app/api/v1/{knowledge,voice,evaluation}/routes.py`, mounted under `/api/v1/*` in `app/main.py`. Key endpoints (absolute paths): `POST /api/v1/knowledge/query`, `GET /api/v1/knowledge/status`, `GET /api/v1/knowledge/context/{query}`. The query route special-cases Anthropic "credit balance too low" into a 502 with a helpful message.

### Frontend — Storylane navigation is the "act" layer
`frontend/app/page.tsx` owns a single `StorylaneController` instance and wires chat + voice into it. **Navigation only fires when the Interactive Dashboard tab is active** (`activeTab === 0`) — chat/voice on other tabs still answer but won't move the iframe (`navigateStorylaneIfVisible`).

- `lib/storylaneMapper.ts` — maps a query to a dashboard section. Two-stage: exact question-string match first (uses a mapping-specific `page_id` URL), then keyword scoring across section keyword lists. **This is where you add/adjust navigation targets** — edit the `URLS` object (page IDs from Storylane share links) and the section keyword lists.
- `lib/storylaneController.ts` — performs navigation by **destroying and recreating the iframe DOM element** with the new `src` (Storylane doesn't reliably respond to plain `src` reassignment). Heavily console-logged for demo debugging.
- `lib/storylaneConfig.ts` — the share ID (`zjalh0zmyhdm`) and base URL. Must stay in sync with backend `STORYLANE_SHARE_ID`.
- `lib/knowledgeClient.ts` — calls the backend RAG endpoint. Note it hits `NEXT_PUBLIC_BACKEND_API_URL` **directly** (default `localhost:8000`), bypassing the `/api/*` → backend rewrite proxy configured in `next.config.mjs`.
- Components: `components/chat/ChatInterface.tsx`, `components/demo/DemoViewer.tsx`, `components/voice/VoiceWidget.tsx` (VAPI Web SDK). MUI + Emotion; `ThemeRegistry.tsx` handles SSR styling.

**Voice vs chat:** the intended design is that both call the same FastAPI RAG agent for answers, with VAPI used for **speech only** (STT in, TTS out via `vapi.say()`). See the VAPI gotcha below — this is only true if the VAPI dashboard assistant is constrained to not answer on its own.

## Gotchas & conventions

- **VAPI can still answer on its own:** the design intends VAPI to be speech-only (answers come from the FastAPI RAG agent via `queryKnowledge` + `vapi.say()`). But the VAPI **dashboard assistant** will speak from its own LLM unless its system prompt/model is constrained to speech-only / "don't answer product questions." If voice gives answers that don't match chat, check the VAPI dashboard assistant config, not this repo.
- **Branding drift:** the product is CrowdStrike Falcon, but Carbon Black leftovers remain in some strings and comments — e.g. the recreated iframe `title="Interactive Carbon Black Dashboard"` in `storylaneController.ts`, the placeholder "Ask a question about Carbon Black…" in `ChatInterface.tsx`, docstrings in `agent.py`, and parts of `docs/PRD.md`. (Note `DemoViewer.tsx`'s iframe title is already the correct "Interactive Dashboard".) Match the CrowdStrike branding in user-facing changes; the Carbon Black text is stale, not intentional.
- **Debug UI:** `page.tsx` has several "Test:" / "Debug:" buttons and a `window.debugTestNavigation` hook for driving navigation during live demos. They're intentional demo scaffolding, not production UI.
- The generation model id is duplicated in `agent.py`; there is no `ANTHROPIC_MODEL` env var yet (it's on the roadmap in `docs/PRD.md`).
- **Backend must be running** (`uvicorn app.main:app --reload`) for the frontend to answer anything — otherwise chat/voice surface `Failed to fetch` from `knowledgeClient`.
- **First boot needs network access:** startup scrapes the Dropbox-hosted docs and (with `OPENAI_API_KEY`) calls OpenAI for embeddings; offline, it falls back to local HuggingFace embeddings and hardcoded product text.
- `docs/PRD.md` is the fullest spec (architecture diagram, user stories, roadmap). `LANGSMITH_EVALUATION_GUIDE.md` covers the eval setup.
