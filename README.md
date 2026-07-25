# AgriSense AI

**IUT 12th ICT Fest — Bdapps Agentic AI Hackathon**

An autonomous agricultural advisor for smallholder farmers in Bangladesh. It holds a conversation to learn a farm's specifics, calls real external tools (weather, RAG, financial calculator, marketplace, price intelligence, disease detection, payment gateway), chains multi-step reasoning across a whole growing season, remembers the farmer across visits, replies in English or Bengali (typed or spoken), and explains every recommendation in terms of the actual data behind it — real weather readings, retrieved agronomy passages, and sourced cost/price figures, not model recall.

## Status

| Tier | Status |
|---|---|
| **Tier 0 — Core** | ✅ Done, verified end-to-end (including through the browser UI, not just curl/`/docs`) |
| **Tier 1 — Advanced** | ✅ Done, verified end-to-end |
| **Tier 2 — Ambitious / bonus** | ✅ Done — all 5 features implemented and tested, with honest caveats noted below |

Everything below is implemented and running against the real backend. Where a Tier 2 feature has a genuine, disclosed limitation (e.g. disease detection has no offline fallback, the payment gateway runs in a local simulator unless real bdapps credentials are supplied), it's called out explicitly rather than glossed over — see [Real vs. mock / estimated data](#real-vs-mock--estimated-data) and [What's left](#whats-left).

### Frontend ↔ backend connection

The frontend (`frontend/src/api/client.js`) talks directly to the FastAPI backend's real endpoints and adapts every response shape in one place, so every UI component renders real data without needing to know about the backend's schema.

- **Conversational intake** works with free text — "My farm is in Rangpur, 2 acres, loamy soil, medium water, budget 60000, Rabi season" typed directly into the chat is parsed by `app/agent/intake.py` (LLM-based, with a deterministic regex fallback) and filled into the farm profile, rather than requiring a structured form. The same free-text channel lets a farmer *correct* a fact later in the conversation ("actually my farm is in Dinajpur now").
- **Persistent memory, but ChatGPT-style sessions.** Every time the app is opened, it starts a brand-new conversation (no old messages reappear) — but the farmer's underlying profile (location, farm size, soil, budget, etc.) is still remembered, because memory is keyed on a separate `farmer_key` (the phone number, or an anonymous `anon_<uuid>` generated client-side for farmers who never gave one) rather than on the conversation itself. A sidebar (`GET /sessions?farmer_key=`) lists past conversations so a farmer can reopen an old one if they want to.
- Proactive alerts, fertilizer/irrigation schedules, and pest risk are all rendered in the UI (Smart Alerts, Season Planner, Agent Activity panels) straight from the same `/chat` response.
- Marketplace comparisons, price intelligence, disease detection, and the payment gateway each have their own page, but are *also* reachable straight from the chat box (e.g. typing "where can I buy urea" or "should I sell my rice now" gets a real, tool-backed answer without needing to leave the conversation).
- A language toggle (`বাং` / `EN`) in the header switches the whole UI and every chat reply between English and Bengali; a microphone button lets a farmer speak instead of type, and a speaker button reads any assistant reply aloud.
- Set `VITE_USE_MOCK=true` in `frontend/.env` to fall back to static mock data for pure UI work with no backend running. (Note: the standalone `api/mocks/` fixture files and `mockAdapter.js` from earlier in development have been removed as dead code now that the app runs against the real backend end-to-end.)

## Tier 0 — Core

| # | Capability | Where |
|---|---|---|
| 1 | Conversational intake, asks only for missing fields | `agent/planner.py`, `agent/intake.py`, `db/repositories/farm_repo.py` |
| 2 | Live weather grounding (real API, real values used) | `tools/weather_tool.py` (Open-Meteo) |
| 3 | Top-3 crop recommendation with suitability/water need/risk/profit | `agent/explainer.py` |
| 4 | Season plan (with real dates — see Tier 1) | `agent/season_calendar.py` |
| 5 | Financial projection, itemized and internally consistent | `tools/finance_calc.py`, `tools/finance_tool.py` |
| 6 | Explained reasoning citing specific inputs | `agent/explainer.py` |
| 7 | Knowledge base + RAG feeding the advice | `data/knowledge_base.py`, `tools/rag_tool.py` (ChromaDB) |
| 8 | Visible agent trace (every tool call, params, raw return) | `db/repositories/tool_log_repo.py`, `GET /history` |

## Tier 1 — Advanced

| # | Capability | Where | Example |
|---|---|---|---|
| 1 | **Persistent memory across sessions** | `Session.farmer_key`, `farm_repo.carry_forward_profile()` | Pass the same `farmer_key` in a brand-new session (no `session_id`, no `profile`) and the farm is remembered — `remembered_profile: true` in the response, `missing_fields: []` on the very first message. |
| 2 | **Proactive, weather-triggered advice** | `agent/proactive.py` | A Sylhet forecast with 28.5mm rain in 1 day produced *"Heavy rain (28.5mm) forecast in 1 day(s)... Delayed land preparation/sowing by 3 days..."* — and the season plan's actual dates shifted, not just the message text. |
| 3 | **Fertilizer & irrigation scheduler** | `tools/fertilizer_scheduler_tool.py`, `tools/irrigation_scheduler_tool.py` | Real Urea/TSP/MoP kg + cost per growth stage (basal / two top-dress splits), plus an organic (cow dung/compost) alternative; irrigation event timing + cost, collapsed to readable growth-stage checkpoints. |
| 4 | **Pest & disease risk, growth-stage aware** | `data/pest_knowledge.py`, `tools/pest_risk_tool.py` | Risk is evaluated per growth stage (establishment / vegetative / flowering / fruiting / preharvest) against the weather actually expected *during that stage* — using the real forecast day when the stage falls within the fetched window, and an honestly-labeled extrapolation from current conditions when it doesn't. E.g. potato late blight only flags when humidity ≥90% and temp is in the 10-20°C band that genuinely favors it, and only in the stages it can actually affect. |
| 5 | **Scenario simulation** | `tools/scenario_simulator_tool.py`, `POST /simulate` | *"What if rainfall drops 30% and budget is cut 40%?"* returns both the original and revised financial projection with a stated explanation, e.g. *"Profit would go down by 28,198 BDT... the farmer could cover about 1.53 acres instead."* |

## Tier 2 — Ambitious / bonus

| # | Capability | Where | Notes |
|---|---|---|---|
| 1 | **Marketplace & supplier comparison** | `tools/marketplace_tool.py`, `api/routes/marketplace.py`, `data/supplier_catalog.py`, `features/marketplace/` | Compares fertilizer/pesticide/seed suppliers on a disclosed composite score (price 40%, delivery 20%, distance 20%, rating 20%), all normalized 0-1 and weighted. Reachable both from its own page and directly from chat ("where can I buy urea"). Supplier data is a seeded mock catalog (per the hackathon brief's own allowance for mock marketplace data) — clearly not live supplier pricing. |
| 2 | **Market price intelligence (sell-now / store-and-wait)** | `tools/price_intelligence_tool.py`, `api/routes/price_intelligence.py`, `features/prices/` | `current_price` comes from the same real, sourced crop-price data used everywhere else (BBS/DAM). The *historical trend* and *projected future price* are a disclosed, illustrative seasonal model (a fixed monthly index scaled to match today's real price), **not measured historical price data** — no free, reliable source for month-by-month crop price history exists, so rather than either fabricating "real" data or skipping the feature, the model is used and labeled as such in the response (`reasoning` field). Perishables never get a "store" recommendation; non-perishables get "store_and_wait" only when the projected gain clears an 8% threshold. Reachable from its own page and directly from chat ("should I sell my rice now"). |
| 3 | **Plant disease detection from images** | `tools/disease_detection_tool.py`, `api/routes/disease_detection.py`, `features/disease/` | Uses OpenAI's vision model (`gpt-4o-mini`) to classify an uploaded leaf/crop photo, then cross-references the result against `data/pest_knowledge.py` when it recognizes a known disease. **This is the one feature with no offline fallback** — it requires `OPENAI_API_KEY` to function at all, unlike every other tool in the app. Every result (known or not) carries an explicit `disclaimer` that it isn't independently verified, and the tool is deliberately honest about uncertainty: tested against a synthetic (non-leaf) image, it correctly returned "unclear/low confidence" rather than confidently hallucinating a diagnosis. |
| 4 | **bdapps Payment Gateway (CaaS)** | `integrations/bdapps_caas.py`, `api/routes/payments.py`, `features/marketplace/SupplierOffersTable.jsx` | Implements the real bdapps CaaS (Charging-as-a-Service) contract — balance query, payment-instrument list, direct debit checkout — from the actual bdapps API spec. If `BDAPPS_APPLICATION_ID` and `BDAPPS_PASSWORD` are set, it calls the real bdapps endpoint first; on any failure (or if credentials are blank, which is the default), it falls back transparently to a local, stateful simulator (a `MobileWallet` DB row standing in for the subscriber's mobile account balance), including realistic failure modes (insufficient balance, a random ~3% simulated temporary error). **Currently running in simulator mode** in this deployment — only an `applicationId` is available, not the paired sandbox password, so the real-API path is wired but unexercised end-to-end; see [What's left](#whats-left). |
| 5 | **Bengali (বাংলা) language & voice interaction** | `agent/i18n.py`, `lib/i18n.js`, `ChatInput.jsx`, `MessageBubble.jsx` | Every deterministic (no-LLM) reply path has fully-written Bengali text (clarifying questions, greetings, fallback replies) so Bengali works with or without an API key, consistent with the Tier 0 "works without an LLM key" rule — when an LLM *is* available, a Bengali-language instruction is appended to its prompts instead of hand-written strings. Voice uses the browser-native Web Speech API (`SpeechRecognition` for mic input, `speechSynthesis` for read-aloud) — no external speech API or key needed, and it respects the current language (`bn-BD` vs `en-US`). |

## Architecture

### Backend

```
backend/app/
├── main.py                    FastAPI app, CORS, startup (create tables + seed crop data)
├── config.py                  Settings (env-driven: DB URL, OpenAI key/model, weather/chroma config, bdapps creds)
│
├── api/routes/                 HTTP layer
│   ├── chat.py                  POST /chat  — main agent entry point
│   ├── weather.py                POST /weather
│   ├── retrieve.py                POST /retrieve  (RAG)
│   ├── calculate.py               POST /calculate (financial calculator)
│   ├── simulate.py                POST /simulate  (Tier 1 scenario simulation)
│   ├── sessions.py                GET /history, GET /sessions (now with a `preview` field for the sidebar)
│   ├── marketplace.py             GET /marketplace  (Tier 2)
│   ├── price_intelligence.py      GET /price-intelligence  (Tier 2)
│   ├── disease_detection.py       POST /disease-detection  (Tier 2, multipart image upload)
│   ├── payments.py                GET /payments/balance, /instruments, /history, POST /payments/checkout (Tier 2)
│   └── health.py                  GET /health
│
├── agent/                      The AI agent
│   ├── core.py                  AgentOrchestrator.handle_turn() — memory → plan → act → explain
│   ├── planner.py                 Ask a question, route chat vs. recommend, pick 3 candidate crops
│   ├── intake.py                   Extracts profile facts from free-text chat (LLM + regex fallback)
│   ├── chat_responder.py           Composes non-recommendation replies: greetings, field lookups,
│   │                                marketplace detection, price-query detection, general RAG-grounded chat
│   ├── executor.py                 Calls tools via the registry, logs every call
│   ├── explainer.py                 Turns tool outputs into reasoning/reply/season plan (LLM or templated)
│   ├── state.py                     AgentDecision / AgentTurn / ToolCallRecord dataclasses
│   ├── season_calendar.py           Tier 1: turns crop duration into real dated stage checkpoints
│   ├── proactive.py                 Tier 1: scans the real forecast, generates + applies weather alerts
│   └── i18n.py                      Tier 2: Bengali strings for every deterministic reply path
│
├── llm/
│   ├── client.py                Thin OpenAI wrapper — every method degrades to None with no API key,
│   │                              plus classify_image_json() for vision (disease detection only)
│   └── prompts/                  system_prompt.py, planning_prompt.py, explanation_prompt.py
│
├── memory/
│   ├── short_term.py             Recent conversation turns for LLM context
│   ├── long_term.py               Known farm-profile facts (never re-asked)
│   └── memory_manager.py          Combines both into one AgentMemory per turn
│
├── tools/                      Pluggable AgriTool implementations
│   ├── base.py                   AgriTool ABC (name, description, input/output schema, run())
│   ├── registry.py                Tool lookup used by the executor
│   ├── weather_tool.py             Open-Meteo integration (geocoding + current + 7-day forecast + humidity)
│   ├── rag_tool.py                 ChromaDB semantic search over the knowledge base
│   ├── finance_calc.py             Shared cost/revenue/ROI math (used by finance + scenario tools)
│   ├── finance_tool.py             Wraps finance_calc.py, reads CropReference from DB
│   ├── fertilizer_scheduler_tool.py  Tier 1: growth-stage Urea/TSP/MoP schedule + organic alt
│   ├── irrigation_scheduler_tool.py  Tier 1: growth-stage irrigation event schedule
│   ├── pest_risk_tool.py             Tier 1: growth-stage-aware, weather-triggered pest/disease risk
│   ├── scenario_simulator_tool.py    Tier 1: "what if" recomputation
│   ├── marketplace_tool.py           Tier 2: supplier comparison, composite scoring
│   ├── price_intelligence_tool.py    Tier 2: sell-now / store-and-wait recommendation
│   ├── disease_detection_tool.py     Tier 2: vision-model image classification
│   ├── crop_data.py                  Seed data for 34 crops (source of truth, loaded into the DB once)
│   └── units.py                      Farm-size unit conversion (acre/bigha/katha/decimal/shotangsho → acres)
│
├── integrations/
│   └── bdapps_caas.py           Tier 2: real bdapps CaaS HTTP client + local simulator fallback
│
├── data/
│   ├── knowledge_base.py         RAG seed passages, each with a real cited source
│   ├── pest_knowledge.py          Pest/disease trigger conditions per crop, per applicable growth stage
│   ├── supplier_catalog.py        Tier 2: seeded mock fertilizer/pesticide/seed supplier catalog
│   └── sources.py                 Full citation registry (BBS, USDA GAIN, DAM, BSFIC, BRRI, BARI...)
│
├── db/
│   ├── models.py                 Session (+farmer_key), Message, FarmProfile, ToolCallLog, SeasonPlan,
│   │                               FinancialProjection, CropReference, MobileWallet, PaymentTransaction
│   └── repositories/               One CRUD module per model (+ payment_repo.py for Tier 2)
│
└── schemas/                    Pydantic request/response contracts (chat, farm_profile, tool_io, payment)
```

### Frontend

```
frontend/src/
├── main.jsx / App.jsx           Entry point, section routing (adds marketplace/prices/disease pages)
├── api/
│   ├── client.js                  All backend calls + response adapters + farmer_key/session helpers
│   └── index.js                    Re-exports client.js (mock adapter removed — real backend only)
├── app/                          MainHeader (+ language toggle), Sidebar, DashboardHome
├── context/
│   ├── store.js                    App state + reducer (session, profile, chat, schedules, language)
│   ├── AppStateContext.jsx          Clears stored session_id on every mount → new chat per app open
│   └── useTranslation.js            useTranslation() hook for the i18n strings below
├── lib/
│   ├── constants.js                 Nav sections (incl. marketplace/prices/disease)
│   └── i18n.js                      English/Bengali UI string dictionary + Web Speech language codes
├── features/
│   ├── chat/                        ChatPanel, ChatSidebar (past conversations), ChatInput (+ mic),
│   │                                  MessageBubble (+ read-aloud), useSendMessage
│   ├── crops/                       Crop recommendation cards
│   ├── timeline/                    SeasonTimeline + FertilizerScheduleTable, IrrigationScheduleList,
│   │                                  PestRiskList (growth-stage grouped)
│   ├── financials/                  FinancialDashboard + DataSourcesCard (confidence/sourcing disclosure)
│   ├── marketplace/                 MarketplacePage, SupplierOffersTable (+ Buy Now checkout flow)
│   ├── prices/                      PriceIntelligencePage (bar-chart of historical/projected prices)
│   ├── disease/                     DiseaseDetectionPage (upload/camera capture, confidence + disclaimer)
│   ├── alerts/                      Smart Alerts
│   ├── weather/                     Weather Analysis
│   └── trace/                       Agent Activity / tool trace panel
└── components/ui/                Shared Button/Card/Badge/Panel/Tabs/etc.
```

### Design choices worth knowing

- **Every tool call is logged** (`ToolCallLog` table) with input, output, status, and latency — this is what the Agent Trace panel renders, and `GET /history` returns it as `tool_trace`. Every tool (weather, RAG, finance, fertilizer/irrigation schedulers, pest risk, scenario simulator, marketplace, price intelligence, disease detection) goes through the same `executor.call_tool()` path, so nothing skips logging.
- **Crop economics live in the database** (`crop_references` table), not a hardcoded dict — seeded once at startup from `crop_data.py`, so prices can be updated without a redeploy.
- **The agent works with or without an OpenAI key**, for everything except disease detection. Every other LLM-backed decision (phrasing a clarifying question, picking candidate crops, writing reasoning, extracting profile facts from chat, translating replies to Bengali) has a deterministic fallback, so `/chat` produces the same *shape* of response either way. Disease detection is the sole, explicitly-documented exception — it needs a real vision model call and has no offline path.
- **The LLM never invents numbers.** Profit, ROI, yield, weather, price, and marketplace figures always come straight from tool outputs and are merged into the response in code; the LLM is only ever asked for text (labels, reasoning, reply wording).
- **Explicit farmer requests are honored deterministically.** If a message names a specific crop (e.g. "I want to plant cabbage"), that crop is force-included as the top pick in code — not just requested via prompt.
- **Internal-consistency guardrails.** The explainer validates that the LLM's `reply` and `season_plan` text actually reference the crop they're labeled as, and falls back to deterministic wording if they don't match.
- **Proactive alerts actually change the plan, not just the message.** When heavy rain overlaps the land-preparation/sowing window, `season_plan`'s dates are recomputed and shifted — the alert text and the calendar agree.
- **Chat intent routing, not a single monolithic pipeline.** `AgentDecision.action` is one of `ask_clarifying_question` / `recommend` / `chat_reply` — a plain "hi", a marketplace question, a price question, or a general agronomy question gets answered directly (`chat_reply`) instead of forcing a full crop-recommendation recomputation on every single message. The full pipeline (`recommend`) only runs on the first complete-profile turn, when the profile actually changed, or when the farmer's message clearly asks for a (re-)recommendation.
- **Sessions vs. memory are deliberately decoupled.** Opening the app always starts a fresh conversation (`localStorage`'s `session_id` is cleared on mount) — but the farmer's profile is looked up by the separate, longer-lived `farmer_key`, so "start fresh but don't forget me" both hold at once. A farmer with no phone number still gets persistence via a generated `anon_<uuid>` key.
- **Tier 2 "try real, fall back to simulator" pattern.** The bdapps payment integration attempts the real HTTP call first whenever credentials are configured, catches any failure, and falls back to a local, stateful simulator — the same code path works in a real sandbox and in a demo with no credentials at all.
- **Disclosed-heuristic pattern, applied consistently.** Wherever no real/free data source exists (rainfall→yield sensitivity, non-rice fertilizer cost scaling, seasonal price curves), a labeled, deterministic model is used instead of either fabricating "real" data or refusing to build the feature — always surfaced via `notes`/`assumptions`/`confidence`/`reasoning`/`disclaimer` fields in the actual API response, not just in this README.

## Real vs. mock / estimated data

**Real, live, called at request time:**
- Weather (Open-Meteo) — actual current conditions + 7-day forecast (temperature, humidity, rainfall) for whatever location is given, no API key needed.
- RAG retrieval (ChromaDB) — real vector search over the seeded knowledge base.
- OpenAI LLM calls (when `OPENAI_API_KEY` is set) — real completions, not canned responses.
- OpenAI vision calls (disease detection, when `OPENAI_API_KEY` is set) — a real image classification call; this feature simply doesn't function without it.
- bdapps CaaS payment calls — real HTTP calls to the real bdapps endpoint, *when* `BDAPPS_APPLICATION_ID`/`BDAPPS_PASSWORD` are both configured; otherwise (the current default) a local simulator stands in.

**Real, sourced, static (not live-fetched, but not invented either):** crop yields and prices (BBS Yearbook of Agricultural Statistics-2024, DAM price notice, BSFIC), fertilizer prices (USDA GAIN report), one real rice fertilizer application-rate study, BRRI/BARI variety facts. Full citations in `app/data/sources.py`. Price intelligence's `current_price` is this same sourced figure.

**Disclosed estimates / heuristics (not sourced, and the code says so):**
- Non-rice fertilizer *cost* is scaled from rice's real dose by a per-crop intensity ratio (`cost_confidence: "mixed"` on every affected record).
- Seed cost, water cost, and per-crop labor-days are smallholder-practice estimates, not from a specific cited survey.
- The fertilizer/irrigation stage-timing split and the 5-stage growth calendar (establishment/vegetative/flowering/fruiting/preharvest) used for pest risk are standard general agronomic practice, not crop-specific citations.
- Pest/disease trigger thresholds are standard IPM (Integrated Pest Management) knowledge, not sourced to a specific paper.
- The scenario simulator's rainfall→yield sensitivity is an explicit heuristic (`RAINFALL_SENSITIVITY` by water-need category), disclosed in the tool's `assumptions` field every time it's used.
- Season-plan dates are computed as offsets from *today*, not each crop's real-world planting calendar for the current date.
- **Marketplace supplier catalog (`data/supplier_catalog.py`) is a seeded mock dataset** — realistic prices/ratings/delivery times, but not live supplier data (the hackathon brief explicitly allows mock marketplace data).
- **Price intelligence's historical/projected price trend is a disclosed synthetic seasonal model**, not measured historical data — a fixed illustrative monthly index (`SEASONAL_INDEX_BY_MONTH`) is scaled to match today's real price. No free, reliable month-by-month crop price history exists to plug in instead; this is stated in the tool's own `reasoning` output field.
- **The payment gateway currently runs in simulator mode** in this deployment (no bdapps sandbox password available, only an application ID) — see [What's left](#whats-left).

Nothing above is presented to the farmer as more certain than it is — `FinanceOutput.data_confidence`/`notes`, `FertilizerScheduleOutput.notes`, `IrrigationScheduleOutput.notes`, `ScenarioSimulationOutput.assumptions`, `PriceIntelligenceOutput.reasoning`, and `DiseaseDetectionOutput.disclaimer` all carry these disclosures into the actual API response.

## Data sources

- **BBS Yearbook of Agricultural Statistics-2024** (Bangladesh Bureau of Statistics) — per-acre yields (FY2023-24) and wholesale/retail prices for all 34 crops
- **DAM price notice** (Department of Agricultural Marketing, Mar 2024) — government-fixed prices, preferred over BBS retail figures where they overlap
- **USDA GAIN Report BG2025-0017** — government-fixed fertilizer prices (Urea/TSP/DAP/MOP)
- **BSFIC** — sugarcane mill-gate purchase price
- **BRRI / BARI** variety data — rice/potato/mustard variety facts in the RAG knowledge base
- A real measured rice fertilizer application study (180-43-42 kg/ha Urea-TSP-MoP) — the one sourced fertilizer-dose figure
- **Open-Meteo** — live weather (no API key required)
- **bdapps CaaS API spec** (hSenid Mobile Solutions / bdapps, "BDApps Pro API Guide", doc v1.1.1) — the real contract the payment integration implements

## Crops covered (34)

Cereals: rice, wheat, maize · Pulses: lentil, gram, mung, mashkalai, khesari · Oilseeds: mustard, sesame, groundnut, soybean, linseed · Spices: garlic, turmeric, ginger, chilli, coriander · Vegetables: potato, tomato, onion, cauliflower, cabbage, brinjal, okra, cucumber, pumpkin, bitter_gourd, carrot, radish, spinach, sweet_potato · Fiber & sugar: jute, sugarcane

## Running the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY for LLM/Bengali/disease-detection features
uvicorn app.main:app --reload
```

Interactive docs: `http://127.0.0.1:8000/docs`

`.env` variables:

| Variable | Purpose | Required? |
|---|---|---|
| `OPENAI_API_KEY` | LLM-enhanced replies, crop selection, Bengali generation, disease detection | Optional — everything except disease detection has a deterministic fallback |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini` | Optional |
| `DATABASE_URL` | Defaults to local SQLite `app.db` | Optional |
| `WEATHER_API_BASE_URL`, `WEATHER_GEOCODING_URL` | Open-Meteo endpoints | Optional (sensible defaults) |
| `CHROMA_PERSIST_DIR`, `CHROMA_COLLECTION_NAME` | RAG vector store location | Optional (sensible defaults) |
| `BDAPPS_APPLICATION_ID`, `BDAPPS_PASSWORD` | Real bdapps CaaS sandbox credentials | Optional — leave blank to use the local payment simulator |
| `BDAPPS_CAAS_BASE_URL` | bdapps CaaS endpoint | Optional (sensible default) |

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat` | Main agent turn — memory, missing-field collection, tool orchestration, recommendations, alerts, schedules, marketplace/price/disease routing |
| POST | `/weather` | Standalone weather lookup (real Open-Meteo data) |
| POST | `/retrieve` | Standalone RAG search over the agronomy knowledge base |
| POST | `/calculate` | Standalone financial calculator for any of the 34 crops |
| POST | `/simulate` | "What if" rainfall/budget scenario recomputation |
| GET | `/history?session_id=` | Full conversation + tool trace + season plans + financial projections for a session |
| GET | `/sessions?farmer_key=` | List sessions (with preview text) for one persistent farmer — powers the chat sidebar |
| GET | `/marketplace` | Tier 2: supplier comparison for a fertilizer/pesticide/seed item |
| GET | `/price-intelligence` | Tier 2: current price + historical/projected trend + sell/store recommendation |
| POST | `/disease-detection` | Tier 2: upload a crop/leaf photo (JPEG/PNG/WEBP, max 8MB) for AI classification |
| GET | `/payments/balance` | Tier 2: mobile wallet balance (real bdapps call or simulator) |
| GET | `/payments/instruments` | Tier 2: available payment instruments for a subscriber |
| POST | `/payments/checkout` | Tier 2: direct-debit a purchase (e.g. a marketplace order) |
| GET | `/payments/history` | Tier 2: past transactions |
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

### Trying Tier 2 features directly

```bash
# Marketplace: compare urea suppliers
curl "localhost:8000/marketplace?item=urea"

# Price intelligence: should I sell my potatoes now?
curl "localhost:8000/price-intelligence?crop=potato"

# Same two, from inside a normal chat turn:
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "where can I buy urea", "farmer_key": "01700000000"
}'
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "should I sell my rice now", "farmer_key": "01700000000"
}'

# Bengali reply:
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "আমার জমির অবস্থা কী?", "farmer_key": "01700000000", "language": "bn"
}'
```

Disease detection requires a real image file, so it's easiest to try from the frontend's Disease Detection page (or `POST /disease-detection` as multipart form data with an `image` file field).

## Running the frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_USE_MOCK=false by default — points at the real backend
npm run dev
```

Open `http://localhost:5173` (backend must already be running on port 8000 — the backend's CORS config allows any `localhost`/`127.0.0.1` port, so a Vite port bump doesn't break it). Chat naturally with the assistant, or use the sidebar to switch between the app's pages: Crop Recommendations, Season Planner, Financial Dashboard, Smart Alerts, Weather Analysis, Marketplace, Prices, Disease Detection, and Agent Activity — all populated from the real backend.

## What's left

- **Disease detection has only been tested against a synthetic (non-leaf) test image**, which correctly produced a low-confidence/unclear result — proving the honesty design works, but a real leaf/pest photo hasn't yet been run through it end-to-end.
- **The bdapps payment gateway is running in simulator mode.** The real-API code path (`integrations/bdapps_caas.py`) is fully implemented against the actual bdapps CaaS contract, but only a `BDAPPS_APPLICATION_ID` is currently available, not its paired sandbox password — so it has not yet been exercised against the real bdapps endpoint end-to-end. Supplying `BDAPPS_PASSWORD` in `.env` is all that's needed to switch it on.
- Some cost components (seed cost, water/irrigation cost, per-crop labor-days, fertilizer dose split timing) remain estimated rather than officially sourced — see [Real vs. mock](#real-vs-mock--estimated-data).
- Price intelligence's historical/projected trend is an illustrative seasonal model, not measured price history — there's no free, reliable data source to replace it with.
- The frontend's `farmerName`/`phoneNumber` fields aren't part of the backend's farm profile (only used locally + as the persistent-memory `farmer_key`) — a farmer's name is never sent to or stored by the backend.
