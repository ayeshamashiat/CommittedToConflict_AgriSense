# AgriSense AI

**IUT 12th ICT Fest — Bdapps Agentic AI Hackathon**

An autonomous agricultural advisor for smallholder farmers in Bangladesh. It holds a conversation to learn a farm's specifics, calls real external tools (weather, RAG, financial calculator, and more), chains multi-step reasoning across a whole growing season, remembers the farmer across visits, and explains every recommendation in terms of the actual data behind it — real weather readings, retrieved agronomy passages, and sourced cost/price figures, not model recall.

## Status

| Part | Status |
|---|---|
| **Backend / APIs / Database** | ✅ Done |
| **AI Agent (Tier 0 + Tier 1)** | ✅ Done |
| **Frontend** | ❌ Not started — `frontend/` is still the untouched Vite scaffold |

Tier 0 (core) and Tier 1 (advanced) are both fully implemented and verified end to end on the backend. **No frontend exists yet** — everything below is exercised via the FastAPI docs (`/docs`) or curl. Tier 2 was not attempted, per the brief's own advice not to spread thin across bonus features.

## Tier 0 — Core (all done)

| # | Capability | Where |
|---|---|---|
| 1 | Conversational intake, asks only for missing fields | `agent/planner.py`, `db/repositories/farm_repo.py` |
| 2 | Live weather grounding (real API, real values used) | `tools/weather_tool.py` (Open-Meteo) |
| 3 | Top-3 crop recommendation with suitability/water need/risk/profit | `agent/explainer.py` |
| 4 | Season plan (now with real dates, see Tier 1 below) | `agent/season_calendar.py` |
| 5 | Financial projection, itemized and internally consistent | `tools/finance_calc.py`, `tools/finance_tool.py` |
| 6 | Explained reasoning citing specific inputs | `agent/explainer.py` |
| 7 | Knowledge base + RAG feeding the advice | `data/knowledge_base.py`, `tools/rag_tool.py` (ChromaDB) |
| 8 | Visible agent trace (every tool call, params, raw return) | `db/repositories/tool_log_repo.py`, `GET /history` |

## Tier 1 — Advanced (all done)

| # | Capability | Where | Example |
|---|---|---|---|
| 1 | **Persistent memory across sessions** | `Session.farmer_key`, `farm_repo.carry_forward_profile()` | Pass the same `farmer_key` in a brand-new session (no `session_id`, no `profile`) and the farm is remembered — `remembered_profile: true` in the response, verified with zero `missing_fields` on the very first message of a new session. |
| 2 | **Proactive, weather-triggered advice** | `agent/proactive.py` | Verified live: a Sylhet forecast with 28.5mm rain in 1 day produced *"Heavy rain (28.5mm) forecast in 1 day(s)... Delayed land preparation/sowing by 3 days to avoid working wet, compacted soil"* — and the season plan's actual dates shifted, not just the message. |
| 3 | **Fertilizer & irrigation scheduler** | `tools/fertilizer_scheduler_tool.py`, `tools/irrigation_scheduler_tool.py` | Real Urea/TSP/MoP kg + cost per growth stage (basal / two top-dress splits), plus an organic (cow dung/compost) alternative; irrigation event timing + cost, collapsed to readable growth-stage checkpoints for long-duration crops. |
| 4 | **Pest & disease risk** | `data/pest_knowledge.py`, `tools/pest_risk_tool.py` | Risk is evaluated against the farm's *actual* fetched temperature/humidity/rainfall, not a static per-crop list — e.g. potato late blight only flags when humidity ≥90% and temp is in the 10-20°C band that genuinely favors it. |
| 5 | **Scenario simulation** | `tools/scenario_simulator_tool.py`, `POST /simulate` | *"What if rainfall drops 30% and budget is cut 40%?"* returns both the original and revised financial projection with a stated explanation, e.g. *"Profit would go down by 28,198 BDT... the farmer could cover about 1.53 acres instead."* |

## Architecture

```
backend/app/
├── main.py                    FastAPI app, CORS, startup (create tables + seed crop data)
├── config.py                  Settings (env-driven: DB URL, OpenAI key/model, weather/chroma config)
│
├── api/routes/                 HTTP layer
│   ├── chat.py                 POST /chat  — main agent entry point
│   ├── weather.py               POST /weather
│   ├── retrieve.py              POST /retrieve  (RAG)
│   ├── calculate.py             POST /calculate (financial calculator)
│   ├── simulate.py              POST /simulate  (Tier 1 scenario simulation)
│   ├── sessions.py              GET /history, GET /sessions
│   └── health.py                GET /health
│
├── agent/                      The AI agent
│   ├── core.py                  AgentOrchestrator.handle_turn() — memory → plan → act → explain
│   ├── planner.py                Ask a question, or pick 3 candidate crops (LLM + deterministic fallback)
│   ├── executor.py               Calls tools via the registry, logs every call
│   ├── explainer.py               Turns tool outputs into reasoning/reply/season plan (LLM or templated)
│   ├── state.py                   AgentDecision / AgentTurn / ToolCallRecord dataclasses
│   ├── season_calendar.py         Tier 1: turns crop duration into real dated stage checkpoints
│   └── proactive.py               Tier 1: scans the real forecast, generates + applies weather alerts
│
├── llm/
│   ├── client.py                Thin OpenAI wrapper — every method degrades to None with no API key
│   └── prompts/                  system_prompt.py, planning_prompt.py, explanation_prompt.py
│
├── memory/
│   ├── short_term.py             Recent conversation turns for LLM context
│   ├── long_term.py              Known farm-profile facts (never re-asked)
│   └── memory_manager.py         Combines both into one AgentMemory per turn
│
├── tools/                      Pluggable AgriTool implementations
│   ├── base.py                   AgriTool ABC (name, description, input/output schema, run())
│   ├── registry.py               Tool lookup used by the executor
│   ├── weather_tool.py           Open-Meteo integration (geocoding + current + 7-day forecast)
│   ├── rag_tool.py               ChromaDB semantic search over the knowledge base
│   ├── finance_calc.py           Shared cost/revenue/ROI math (used by finance + scenario tools)
│   ├── finance_tool.py           Wraps finance_calc.py, reads CropReference from DB
│   ├── fertilizer_scheduler_tool.py  Tier 1: growth-stage Urea/TSP/MoP schedule + organic alt
│   ├── irrigation_scheduler_tool.py  Tier 1: growth-stage irrigation event schedule
│   ├── pest_risk_tool.py          Tier 1: weather-triggered pest/disease risk
│   ├── scenario_simulator_tool.py Tier 1: "what if" recomputation
│   ├── crop_data.py              Seed data for 34 crops (source of truth, loaded into the DB once)
│   └── units.py                  Farm-size unit conversion (acre/bigha/katha/decimal/shotangsho → acres)
│
├── data/
│   ├── knowledge_base.py         RAG seed passages, each with a real cited source
│   ├── pest_knowledge.py         Tier 1: pest/disease trigger conditions per crop
│   └── sources.py                Full citation registry (BBS, USDA GAIN, DAM, BSFIC, BRRI, BARI...)
│
├── db/
│   ├── models.py                 Session (+farmer_key), Message, FarmProfile, ToolCallLog,
│   │                              SeasonPlan, FinancialProjection, CropReference
│   └── repositories/              One CRUD module per model
│
└── schemas/                    Pydantic request/response contracts (chat, farm_profile, tool_io)
```

### Design choices worth knowing

- **Every tool call is logged** (`ToolCallLog` table) with input, output, status, and latency — this is what a frontend Agent Trace panel would render, and `GET /history` already returns it as `tool_trace`. All 7 tools (weather, RAG, finance, fertilizer scheduler, irrigation scheduler, pest risk, scenario simulator) go through the same `executor.call_tool()` path, so nothing skips logging.
- **Crop economics live in the database** (`crop_references` table), not a hardcoded dict — seeded once at startup from `crop_data.py`, so prices can be updated without a redeploy.
- **The agent works with or without an OpenAI key.** Every LLM-backed decision (phrasing a clarifying question, picking candidate crops, writing reasoning) has a deterministic fallback, so `/chat` produces the same *shape* of response either way — the LLM improves quality, it isn't load-bearing. Verified both ways during development.
- **The LLM never invents numbers.** Profit, ROI, yield, and weather figures always come straight from tool outputs and are merged into the response in code; the LLM is only ever asked for text (labels, reasoning, reply wording).
- **Explicit farmer requests are honored deterministically.** If a message names a specific crop (e.g. "I want to plant cabbage"), that crop is force-included as the top pick in code — not just requested via prompt — so it holds even without an LLM.
- **Internal-consistency guardrails.** The explainer validates that the LLM's `reply` and `season_plan` text actually reference the crop they're labeled as (a real failure mode hit during testing — the LLM once wrote a "Cabbage" season plan describing jute) and falls back to deterministic wording if they don't match.
- **Proactive alerts actually change the plan, not just the message.** When heavy rain overlaps the land-preparation/sowing window, `season_plan`'s dates are recomputed and shifted — the alert text and the calendar agree.

## Real vs. mock / estimated data

Per the submission requirements, here's exactly what's real and what isn't:

**Real, live, called at request time:**
- Weather (Open-Meteo) — actual current conditions + 7-day forecast for whatever location is given, no API key needed, no caching of fake values.
- RAG retrieval (ChromaDB) — real vector search over the seeded knowledge base.
- OpenAI LLM calls (when `OPENAI_API_KEY` is set) — real completions, not canned responses.

**Real, sourced, static (not live-fetched, but not invented either):** crop yields and prices (BBS Yearbook of Agricultural Statistics-2024, DAM price notice, BSFIC), fertilizer prices (USDA GAIN report), one real rice fertilizer application-rate study, BRRI/BARI variety facts. Full citations in `app/data/sources.py`.

**Disclosed estimates / heuristics (not sourced, and the code says so):**
- Non-rice fertilizer *cost* is scaled from rice's real dose by a per-crop intensity ratio (`cost_confidence: "mixed"` on every affected record) — the official FRG-2018 guide that would give exact per-crop doses blocks automated fetching.
- Seed cost, water cost, and per-crop labor-days are smallholder-practice estimates, not from a specific cited survey.
- The fertilizer/irrigation stage-timing split (3 fertilizer stages, growth-stage irrigation checkpoints) is standard general agronomic practice, not a crop-specific citation.
- Pest/disease trigger thresholds are standard IPM (Integrated Pest Management) knowledge, not sourced to a specific paper.
- The scenario simulator's rainfall→yield sensitivity is an explicit, disclosed heuristic (`RAINFALL_SENSITIVITY` by water-need category) — there's no sourced crop-yield-vs-rainfall model to plug in instead, and the tool's output says so in its `assumptions` field every time it's used.
- Season-plan dates are computed as offsets from *today* (today = start of land prep, +7 days = sowing, etc.), not tied to each crop's actual real-world planting calendar for the current date — there's no persisted "season start" carried across turns yet.

Nothing in the above list is presented to the farmer as more certain than it is — `FinanceOutput.data_confidence`/`notes`, `FertilizerScheduleOutput.notes`, `IrrigationScheduleOutput.notes`, and `ScenarioSimulationOutput.assumptions` all carry this disclosure into the actual API response, not just this README.

## Data sources

- **BBS Yearbook of Agricultural Statistics-2024** (Bangladesh Bureau of Statistics) — per-acre yields (FY2023-24) and wholesale/retail prices for all 34 crops
- **DAM price notice** (Department of Agricultural Marketing, Mar 2024) — government-fixed prices, preferred over BBS retail figures where they overlap
- **USDA GAIN Report BG2025-0017** — government-fixed fertilizer prices (Urea/TSP/DAP/MOP)
- **BSFIC** — sugarcane mill-gate purchase price
- **BRRI / BARI** variety data — rice/potato/mustard variety facts in the RAG knowledge base
- A real measured rice fertilizer application study (180-43-42 kg/ha Urea-TSP-MoP) — the one sourced fertilizer-dose figure; used both for the financial calculator and as the base the fertilizer scheduler splits into growth stages
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
| POST | `/chat` | Main agent turn — memory, missing-field collection, tool orchestration, recommendations, alerts, schedules |
| POST | `/weather` | Standalone weather lookup (real Open-Meteo data) |
| POST | `/retrieve` | Standalone RAG search over the agronomy knowledge base |
| POST | `/calculate` | Standalone financial calculator for any of the 34 crops |
| POST | `/simulate` | Tier 1: "what if" rainfall/budget scenario recomputation |
| GET | `/history?session_id=` | Full conversation + tool trace + season plans + financial projections for a session |
| GET | `/sessions?farmer_key=` | List sessions, optionally filtered to one persistent farmer |
| GET | `/health` | Liveness check |

### Trying persistent memory

```bash
# Turn 1 — new farmer, full profile
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "advice please",
  "farmer_key": "01700000000",
  "profile": {"location": "Bogura", "farm_size": 3, "soil_type": "sandy loam",
              "water_availability": "low", "budget": 40000, "target_season": "Rabi"}
}'

# Turn 2 — SAME farmer_key, brand-new session, no profile given
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "what should I grow now",
  "farmer_key": "01700000000"
}'
# -> remembered_profile: true, missing_fields: [], straight to recommendations
```

## What's left

- **Frontend**: chat interface, farmer profile panel, crop recommendation cards, season timeline, financial dashboard, and Agent Trace panel — none of this exists yet beyond the Vite scaffold in `frontend/`.
- **Tier 2** (marketplace, market price intelligence, image disease detection, bdapps payment gateway, Bengali/voice) — not attempted, per the brief's guidance to solidify Tier 0/1 first.
- Some cost components (seed cost, water/irrigation cost, per-crop labor-days, fertilizer dose split timing) remain estimated rather than officially sourced — see "Real vs. mock" above.
