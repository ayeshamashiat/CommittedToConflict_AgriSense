# AgriSense AI

An agentic crop-advisory assistant for smallholder farmers in Bangladesh, built for the IUT Bdapps Agentic AI Hackathon. A farmer describes their farm (location, size, soil, water, budget, season) in conversation; the agent asks for whatever's missing, then grounds its recommendations in real weather data, retrieved agronomy knowledge, and a financial calculator — producing top-3 crop recommendations with reasoning, a season plan, and a financial summary.

## Status

| Part | Status |
|---|---|
| **Backend / APIs / Database** (Member B) | ✅ Done |
| **AI Agent** (Member A) | ✅ Done |
| **Frontend** (Member C) | ❌ Not started — `frontend/` is still the untouched Vite scaffold |

Tier 0 requirements are fully met on the backend/agent side. Nothing in `frontend/` beyond initial scaffolding exists yet — that's the remaining work.

## Architecture

```
backend/app/
├── main.py                  FastAPI app, CORS, startup (create tables + seed crop data)
├── config.py                Settings (env-driven: DB URL, OpenAI key/model, weather/chroma config)
│
├── api/routes/               HTTP layer
│   ├── chat.py               POST /chat  — main agent entry point
│   ├── weather.py            POST /weather
│   ├── retrieve.py           POST /retrieve  (RAG)
│   ├── calculate.py          POST /calculate (financial calculator)
│   ├── sessions.py           GET /history, GET /sessions
│   └── health.py             GET /health
│
├── agent/                    The AI agent (Member A)
│   ├── core.py                AgentOrchestrator.handle_turn() — memory → plan → act → explain
│   ├── planner.py             Ask a question, or pick 3 candidate crops (LLM + deterministic fallback)
│   ├── executor.py            Calls tools via the registry, logs every call
│   ├── explainer.py           Turns tool outputs into reasoning/reply/season plan (LLM or templated)
│   └── state.py               AgentDecision / AgentTurn / ToolCallRecord dataclasses
│
├── llm/
│   ├── client.py              Thin OpenAI wrapper — every method degrades to None with no API key
│   └── prompts/                system_prompt.py, planning_prompt.py, explanation_prompt.py
│
├── memory/
│   ├── short_term.py           Recent conversation turns for LLM context
│   ├── long_term.py            Known farm-profile facts (never re-asked)
│   └── memory_manager.py       Combines both into one AgentMemory per turn
│
├── tools/                    Pluggable AgriTool implementations (weather / RAG / finance)
│   ├── base.py                 AgriTool ABC (name, description, input/output schema, run())
│   ├── registry.py             Tool lookup used by the executor
│   ├── weather_tool.py         Open-Meteo integration (geocoding + current + 7-day forecast)
│   ├── rag_tool.py             ChromaDB semantic search over the knowledge base
│   ├── finance_tool.py         Cost/revenue/profit/ROI/break-even, reads CropReference from DB
│   ├── crop_data.py            Seed data for 34 crops (source of truth, loaded into the DB once)
│   └── units.py                Farm-size unit conversion (acre/bigha/katha/decimal/shotangsho → acres)
│
├── data/
│   ├── knowledge_base.py       RAG seed passages, each with a real cited source
│   └── sources.py               Full citation registry (BBS, USDA GAIN, DAM, BSFIC, BRRI, BARI...)
│
├── db/
│   ├── models.py                Session, Message, FarmProfile, ToolCallLog, SeasonPlan,
│   │                             FinancialProjection, CropReference
│   └── repositories/            One CRUD module per model
│
└── schemas/                   Pydantic request/response contracts (chat, farm_profile, tool_io)
```

### Design choices worth knowing

- **Every tool call is logged** (`ToolCallLog` table) with input, output, status, and latency — this is what powers the frontend's planned Agent Trace panel, and `GET /history` already returns it as `tool_trace`.
- **Crop economics live in the database** (`crop_references` table), not a hardcoded dict — seeded once at startup from `crop_data.py`, so prices can be updated without a redeploy.
- **The agent works with or without an OpenAI key.** Every LLM-backed decision (phrasing a clarifying question, picking candidate crops, writing reasoning) has a deterministic fallback, so `/chat` produces the same *shape* of response either way — the LLM improves quality, it isn't load-bearing.
- **The LLM never invents numbers.** Profit, ROI, yield, and weather figures always come straight from tool outputs and are merged into the response in code; the LLM is only ever asked for text (labels, reasoning, reply wording).
- **Explicit farmer requests are honored deterministically.** If a message names a specific crop (e.g. "I want to plant cabbage"), that crop is force-included as the top pick in code — not just requested via prompt — so it holds even without an LLM.
- **Internal-consistency guardrails.** The explainer validates that the LLM's `reply` and `season_plan` text actually reference the crop they're labeled as (a real failure mode encountered during testing — the LLM once wrote a "Cabbage" season plan describing jute) and falls back to deterministic wording if they don't match.

## Data sources

Every number in `crop_data.py` and `knowledge_base.py` is either real and cited, or explicitly flagged as an estimate — see `app/data/sources.py` for full citations. Primary sources:

- **BBS Yearbook of Agricultural Statistics-2024** (Bangladesh Bureau of Statistics) — per-acre yields (FY2023-24) and wholesale/retail prices for all 34 crops
- **DAM price notice** (Department of Agricultural Marketing, Mar 2024) — government-fixed prices, preferred over BBS retail figures where they overlap
- **USDA GAIN Report BG2025-0017** — government-fixed fertilizer prices (Urea/TSP/DAP/MOP)
- **BSFIC** — sugarcane mill-gate purchase price
- **BRRI / BARI** variety data — rice/potato/mustard variety facts in the RAG knowledge base
- A real measured rice fertilizer application study — the one sourced fertilizer-dose figure; other crops' fertilizer cost is estimated by scaling this ratio (flagged `cost_confidence: "mixed"`)
- **Open-Meteo** — live weather (no API key required)

## Crops covered (34)

Cereals: rice, wheat, maize · Pulses: lentil, gram, mung, mashkalai, khesari · Oilseeds: mustard, sesame, groundnut, soybean, linseed · Spices: garlic, turmeric, ginger, chilli, coriander · Vegetables: potato, tomato, onion, cauliflower, cabbage, brinjal, okra, cucumber, pumpkin, bitter_gourd, carrot, radish, spinach, sweet_potato · Fiber & sugar: jute, sugarcane

## Running the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY if you want LLM-enhanced responses
uvicorn app.main:app --reload
```

Interactive docs: `http://127.0.0.1:8000/docs`

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat` | Main agent turn — memory, missing-field collection, tool orchestration, recommendations |
| POST | `/weather` | Standalone weather lookup (real Open-Meteo data) |
| POST | `/retrieve` | Standalone RAG search over the agronomy knowledge base |
| POST | `/calculate` | Standalone financial calculator for any of the 34 crops |
| GET | `/history?session_id=` | Full conversation + tool trace + season plans + financial projections for a session |
| GET | `/sessions` | List all sessions |
| GET | `/health` | Liveness check |

## What's left

- **Frontend (Member C)**: chat interface, farmer profile panel, crop recommendation cards, season timeline, financial dashboard, and Agent Trace panel — none of this exists yet beyond the Vite scaffold in `frontend/`.
- Some cost components (seed cost, water/irrigation cost, per-crop labor-days, fertilizer dose for non-rice crops) remain estimated rather than officially sourced — the official FRG-2018 fertilizer guide blocks automated fetching and would need a manual download to close this gap.
