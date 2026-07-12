# DemoPilot

Interactive product demo agent for CrowdStrike Falcon. Users ask questions via **chat** or **voice**, a RAG-backed knowledge agent answers from product documentation, and the UI navigates a **Storylane** dashboard to the relevant section.

See [docs/PRD.md](./docs/PRD.md) for the system architecture diagram and full product requirements.

## Features

- **Interactive dashboard** — Storylane demo embedded in the UI with query-driven navigation
- **Chat interface** — RAG answers from CrowdStrike Falcon documentation
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

scripts/
  export_retrievals.py        # Export golden-set retrievals -> eval_results/retrievals.json

.claude/                      # Claude Code hook + subagent for retrieval evals
  agents/eval-runner.md       # Retrieval-eval subagent (produces retrievals.json)
  hooks/                      # PostToolUse hook: runs export on retrieval-logic edits
  settings.json               # Wires the hook to Edit/Write

eval_results/                 # Retrieval export output (gitignored)

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

## How I used Claude Code hooks and subagents to iterate on this pipeline

This repo already had generation-quality evals (LangSmith LLM-as-judge, see `LANGSMITH_EVALUATION_GUIDE.md`). It didn't have a retrieval-quality layer, so I closed that gap using Claude Code's hook and subagent primitives rather than a manual "remember to re-run the eval script" habit.

Setup:

* `.claude/agents/eval-runner.md` -- a subagent scoped to retrieval evaluation only, kept separate from generation evaluation so the two don't get conflated.
* `.claude/hooks/trigger-eval-on-retrieval-change.sh` -- a `PostToolUse` hook that fires automatically whenever `app/core/knowledge/agent.py` or `html_extractor.py` (the files that own chunking, embedding, and FAISS retrieval) get edited. It delegates to `eval-runner` in the background.
* `scripts/export_retrievals.py` -- runs in the app's own environment, re-scrapes the CrowdStrike docs, rebuilds the FAISS index with the current chunking config, and writes retrieved contexts for the golden question set to `eval_results/retrievals.json`. It does not score anything -- no RAGAS, no MLflow, no LLM judge calls happen locally.
* A Databricks notebook reads `retrievals.json` and scores it with RAGAS (`LLMContextPrecisionWithoutReference`, using Claude Haiku as the judge model), logging every run to MLflow so retrieval quality is a trend across pipeline edits, not a single point-in-time number.

The point of the hook is that it's deterministic: the export runs whether or not I remember to run it, because it's wired to the edit itself rather than to my own discipline. Scoring currently requires a manual step in the Databricks notebook -- RAGAS scoring runs in an isolated environment on purpose, since it has a dependency chain (`ragas` requires `langchain-community<0.4`) that's incompatible with this app's pinned `langchain 0.3.x` stack, so keeping it separate avoids destabilizing the working app.

Current baseline (Databricks-logged, RAGAS context precision): `context_precision = 20.8%` over the CrowdStrike golden question set, chunk_size=1000, chunk_overlap=200. Logged via MLflow to a Databricks experiment. Context recall is scoped as a known next step -- it requires a labeled reference-answer set per question, which the current golden set doesn't yet include (`LLMContextPrecisionWithoutReference` doesn't need one, which is why precision shipped first).

Goal-based loop for parameter tuning: Rather than manually sweeping `chunk_size` / `chunk_overlap` by hand, I used a goal-based loop to let Claude Code iterate, with an explicit human checkpoint between attempts -- since RAGAS scoring runs in an isolated Databricks notebook rather than being callable directly from Claude Code today, the loop pauses for a scored result instead of running fully autonomously:

```
/goal Tune chunk_size and chunk_overlap in app/core/knowledge/agent.py to
maximize context_precision. After each change, run
scripts/export_retrievals.py to produce fresh retrievals, then STOP and
ask me to run the Databricks scoring notebook and report back the
context_precision value before trying the next configuration. Try at
most 2 configurations total. Report both configurations tried and the
winning one when done.
```

Capping this at 2 configurations was a deliberate choice for this demo, not a limitation of the pattern -- it bounds the loop to a small, observable sweep so each iteration and its reasoning stays easy to walk through live, rather than optimizing for the largest possible search.

Closing this loop end-to-end (Claude Code triggering Databricks scoring directly, e.g. via the MLflow API, rather than pausing for a manual notebook run) is the natural next step toward a fully autonomous goal-based loop.

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
