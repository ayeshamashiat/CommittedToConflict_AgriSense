// Talks to the AgriSense FastAPI backend (backend/app/main.py) and adapts its
// response shape (snake_case, backend data model) into exactly the shape the
// UI components consume (camelCase).

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const SESSION_STORAGE_KEY = 'agrisense:session_id'
const FARMER_KEY_STORAGE_KEY = 'agrisense:farmer_key'

export function getStoredSessionId() {
  try {
    return localStorage.getItem(SESSION_STORAGE_KEY)
  } catch {
    return null
  }
}

export function storeSessionId(id) {
  try {
    if (id) localStorage.setItem(SESSION_STORAGE_KEY, id)
  } catch {
    // localStorage unavailable — session_id just won't survive a reload
  }
}

// Every new chat gets its own backend session_id (see clearStoredSessionId),
// but the backend's Tier 1 memory (carry_forward_profile) only reconnects a
// new session to the farmer's prior profile if it's tagged with the SAME
// farmer_key. phoneNumber makes the best farmer_key when the farmer has given
// one (it's portable across devices), but most farmers won't have typed it in
// — so this device gets a standing anonymous key the first time it's needed,
// persisted independently of any one session, ensuring memory still survives
// starting a new chat even with no phone number on file.
function getOrCreateAnonymousFarmerKey() {
  try {
    let key = localStorage.getItem(FARMER_KEY_STORAGE_KEY)
    if (!key) {
      key = `anon_${crypto.randomUUID()}`
      localStorage.setItem(FARMER_KEY_STORAGE_KEY, key)
    }
    return key
  } catch {
    return undefined
  }
}

// Same precedence sendChatMessage uses (phoneNumber wins if given) — exported
// so the chat sidebar can look up "this farmer's" session list independently
// of sending a message.
export function getFarmerKey(farmerProfile) {
  return farmerProfile?.phoneNumber || getOrCreateAnonymousFarmerKey()
}

// Starting a new chat should get a brand new backend session (fresh
// conversation), while the farmer's remembered profile carries forward via
// farmer_key — this only clears the session id, never the farmer key.
export function clearStoredSessionId() {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {
    // localStorage unavailable — nothing to clear
  }
}

// Full demo reset: unlike clearStoredSessionId (new chat, same remembered
// farmer), this also drops the anonymous farmer_key itself so the next
// session starts with no carried-forward profile at all.
export function clearFarmerIdentity() {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY)
    localStorage.removeItem(FARMER_KEY_STORAGE_KEY)
  } catch {
    // localStorage unavailable — nothing to clear
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = body?.detail
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg ?? JSON.stringify(d)).join('; ')
      : (detail ?? `${res.status} ${res.statusText}`)
    throw new Error(`Request to ${path} failed: ${message}`)
  }
  return res.json()
}

// ---- Farmer profile: frontend (camelCase) <-> backend (snake_case) --------

function toBackendProfile(farmerProfile) {
  if (!farmerProfile) return undefined
  const profile = {}
  if (farmerProfile.location) profile.location = farmerProfile.location
  if (farmerProfile.farmSizeAcres != null) {
    profile.farm_size = farmerProfile.farmSizeAcres
    profile.farm_size_unit = 'acre'
  }
  if (farmerProfile.soilType) profile.soil_type = farmerProfile.soilType
  if (farmerProfile.waterAvailability) profile.water_availability = farmerProfile.waterAvailability
  if (farmerProfile.budgetBDT != null) profile.budget = farmerProfile.budgetBDT
  if (farmerProfile.season) profile.target_season = farmerProfile.season
  return Object.keys(profile).length ? profile : undefined
}

// The profile form's Soil Type / Water Availability <select> elements only
// recognize a fixed, capitalized vocabulary (see SOIL_TYPES/WATER_LEVELS in
// FarmDetailsForm.jsx). Chat intake (agent/intake.py) extracts free-text or
// lowercase values instead ("loamy soil", "medium") since that's what an LLM
// or regex naturally produces from prose — normalize here so a value the
// farmer already gave in chat shows up selected instead of blank "Select…".
const SOIL_TYPE_KEYWORDS = [
  ['sandy', 'Sandy'],
  ['loam', 'Loamy'],
  ['clay', 'Clay'],
  ['silt', 'Silty'],
  ['peat', 'Peaty'],
]

function normalizeSoilType(text) {
  if (!text) return ''
  const lower = text.toLowerCase()
  const match = SOIL_TYPE_KEYWORDS.find(([kw]) => lower.includes(kw))
  return match ? match[1] : ''
}

function normalizeWaterLevel(text) {
  if (!text) return ''
  const lower = text.toLowerCase()
  if (lower.includes('low')) return 'Low'
  if (lower.includes('medium') || lower.includes('med')) return 'Medium'
  if (lower.includes('high')) return 'High'
  return ''
}

function fromBackendProfile(backendProfile, priorFrontendProfile) {
  return {
    // farmerName/phoneNumber aren't part of the backend's FarmProfile (it
    // only tracks location/soil/water/budget/season) — keep whatever the
    // farmer already entered for those two locally.
    farmerName: priorFrontendProfile?.farmerName ?? '',
    phoneNumber: priorFrontendProfile?.phoneNumber ?? '',
    location: backendProfile?.location ?? '',
    farmSizeAcres: backendProfile?.farm_size ?? null,
    budgetBDT: backendProfile?.budget ?? null,
    soilType: normalizeSoilType(backendProfile?.soil_type),
    waterAvailability: normalizeWaterLevel(backendProfile?.water_availability),
    season: backendProfile?.target_season ?? '',
  }
}

// ---- Suitability / risk text -> the fixed High/Medium/Low badge vocabulary the UI expects ----

function normalizeLevel(text) {
  const s = (text ?? '').toString().toLowerCase()
  if (s.includes('excellent') || s.includes('good')) return 'High'
  if (s.includes('moderate')) return 'Medium'
  if (s.includes('risky') || s.includes('poor')) return 'Low'
  if (s.startsWith('high')) return 'High'
  if (s.startsWith('medium')) return 'Medium'
  if (s.startsWith('low')) return 'Low'
  return 'Medium'
}

function capitalize(s) {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function mapRecommendations(recommendations) {
  return (recommendations ?? []).map((r, i) => ({
    id: `crop_${i}_${r.crop_name}`,
    cropName: r.crop_name,
    suitability: normalizeLevel(r.suitability),
    riskLevel: normalizeLevel(r.risk_level),
    waterNeed: capitalize(r.water_need),
    estimatedProfitBDT: r.estimated_profit ?? 0,
    reasoning: r.reasoning,
  }))
}

// ---- Season plan (one object, backend) -> timeline stages (array, frontend) ----

const TIMELINE_STAGES = [
  { id: 'land_preparation', name: 'Land Preparation', dateKey: 'land_preparation_date', notesKey: 'land_preparation' },
  { id: 'sowing', name: 'Sowing', dateKey: 'sowing_date', notesKey: 'sowing' },
  { id: 'fertilizer', name: 'Fertilizer', dateKey: 'fertilizer_date', notesKey: 'fertilizer' },
  { id: 'irrigation', name: 'Irrigation', dateKey: 'sowing_date', notesKey: 'irrigation' },
  { id: 'pest_checks', name: 'Pest Checks', dateKey: 'pest_check_date', notesKey: 'pest_checks' },
  { id: 'harvest', name: 'Harvest', dateKey: 'harvest_date', notesKey: 'harvest' },
]

function mapTimeline(seasonPlan) {
  if (!seasonPlan) return []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  let currentAssigned = false

  return TIMELINE_STAGES.map(({ id, name, dateKey, notesKey }) => {
    const dateStr = seasonPlan[dateKey] ?? null
    let status = 'upcoming'
    if (dateStr) {
      const d = new Date(dateStr)
      if (d < today) status = 'completed'
      else if (!currentAssigned) {
        status = 'current'
        currentAssigned = true
      }
    }
    return {
      id,
      name,
      startDate: dateStr,
      endDate: dateStr,
      status,
      notes: seasonPlan[notesKey] ?? '',
    }
  })
}

// ---- Financial summary ----

function mapFinancials(financialSummary) {
  if (!financialSummary) return null
  const breakEvenDate = financialSummary.break_even_days != null
    ? new Date(Date.now() + financialSummary.break_even_days * 86400000).toISOString()
    : null

  return {
    costs: [
      { label: 'Seeds', amountBDT: financialSummary.seed_cost },
      { label: 'Fertilizer', amountBDT: financialSummary.fertilizer_cost },
      { label: 'Labor', amountBDT: financialSummary.labor_cost },
      { label: 'Water / Irrigation', amountBDT: financialSummary.water_cost },
    ],
    totalCostBDT: financialSummary.total_cost,
    expectedRevenueBDT: financialSummary.revenue,
    netProfitBDT: financialSummary.profit,
    roiPercent: financialSummary.roi_percent,
    breakEvenUnits: financialSummary.break_even_days != null ? `${financialSummary.break_even_days} days` : '—',
    breakEvenDate,
    withinBudget: financialSummary.within_budget,
    dataConfidence: financialSummary.data_confidence,
    yieldSource: financialSummary.yield_source,
    priceSource: financialSummary.price_source,
    notes: financialSummary.notes,
  }
}

// ---- Fertilizer / irrigation schedules, pest risk (Tier 1 tools) ----------
// These come straight from the fertilizer_scheduler / irrigation_scheduler /
// pest_risk_assessor tool outputs (see backend/app/schemas/tool_io.py) — the
// same real, agent-computed figures visible in the Agent Activity trace, not
// separately invented for display.

function mapFertilizerSchedule(schedule) {
  if (!schedule) return null
  return {
    cropName: schedule.crop?.replace(/_/g, ' '),
    stages: (schedule.stages ?? []).map((s) => ({
      stage: s.stage,
      daysAfterSowing: s.days_after_sowing,
      ureaKg: s.urea_kg,
      tspKg: s.tsp_kg,
      mopKg: s.mop_kg,
      costBDT: s.cost_bdt,
      organicAlternative: s.organic_alternative,
    })),
    totalCostBDT: schedule.total_cost_bdt,
    dataConfidence: schedule.data_confidence,
    notes: schedule.notes,
  }
}

function mapIrrigationSchedule(schedule) {
  if (!schedule) return null
  return {
    cropName: schedule.crop?.replace(/_/g, ' '),
    events: (schedule.events ?? []).map((e) => ({
      stage: e.stage,
      daysAfterSowing: e.days_after_sowing,
      note: e.note,
      costBDT: e.cost_bdt,
    })),
    totalCostBDT: schedule.total_cost_bdt,
    notes: schedule.notes,
  }
}

function mapPestRisks(pestRisks) {
  if (!pestRisks) return null
  return {
    cropName: pestRisks.crop?.replace(/_/g, ' '),
    risks: (pestRisks.risks ?? []).map((r) => ({
      name: r.name,
      kind: r.kind,
      riskLevel: r.risk_level,
      growthStage: r.growth_stage,
      daysAfterSowing: r.days_after_sowing,
      triggerReason: r.trigger_reason,
      prevention: r.prevention,
      treatment: r.treatment,
      costBDT: r.estimated_cost_bdt,
    })),
    source: pestRisks.source,
  }
}

// ---- Marketplace & supplier comparison (Tier 2) ---------------------------

function mapMarketplaceOffers(data) {
  if (!data) return null
  return {
    item: data.item,
    unit: data.unit,
    offers: (data.offers ?? []).map((o) => ({
      supplierName: o.supplier_name,
      district: o.district,
      pricePerUnit: o.price_per_unit,
      unit: o.unit,
      deliveryDays: o.delivery_days,
      distanceKm: o.distance_km,
      rating: o.rating,
      estimatedTotalCostBDT: o.estimated_total_cost,
      compositeScore: o.composite_score,
    })),
    rankingMethod: data.ranking_method,
    source: data.source,
    distanceNote: data.distance_note,
  }
}

export async function fetchMarketplace({ item, crop, quantity, location, sessionId }) {
  const params = new URLSearchParams({ item })
  if (crop) params.set('crop', crop)
  if (quantity != null) params.set('quantity', String(quantity))
  if (location) params.set('location', location)
  if (sessionId) params.set('session_id', sessionId)
  const data = await request(`/marketplace?${params.toString()}`)
  return mapMarketplaceOffers(data)
}

// ---- bdapps CaaS payment gateway (Tier 2, sandbox/simulator) --------------

export async function fetchWalletBalance(subscriberId) {
  const params = new URLSearchParams({ subscriber_id: subscriberId })
  const data = await request(`/payments/balance?${params.toString()}`)
  return {
    statusCode: data.statusCode,
    statusDetail: data.statusDetail,
    chargeableBalanceBDT: data.chargeableBalance != null ? Number(data.chargeableBalance) : null,
    accountType: data.accountType,
  }
}

export async function checkout({ subscriberId, amount, purpose, sessionId }) {
  const data = await request('/payments/checkout', {
    method: 'POST',
    body: JSON.stringify({
      subscriber_id: subscriberId,
      amount,
      purpose,
      session_id: sessionId,
    }),
  })
  return {
    success: data.statusCode === 'S1000',
    statusCode: data.statusCode,
    statusDetail: data.statusDetail,
    externalTrxId: data.externalTrxId,
    internalTrxId: data.internalTrxId,
    referenceId: data.referenceId,
    timestamp: data.timeStamp,
    newBalanceBDT: data.newBalance != null ? Number(data.newBalance) : null,
  }
}

export async function fetchPaymentHistory(subscriberId) {
  const params = new URLSearchParams({ subscriber_id: subscriberId })
  const rows = await request(`/payments/history?${params.toString()}`)
  return rows.map((r) => ({
    externalTrxId: r.external_trx_id,
    referenceId: r.reference_id,
    amountBDT: r.amount,
    purpose: r.purpose,
    statusCode: r.status_code,
    statusDetail: r.status_detail,
    createdAt: r.created_at,
  }))
}

// ---- Market price intelligence (Tier 2) -----------------------------------

export async function fetchPriceIntelligence(crop, sessionId) {
  const params = new URLSearchParams({ crop })
  if (sessionId) params.set('session_id', sessionId)
  const data = await request(`/price-intelligence?${params.toString()}`)
  return {
    crop: data.crop,
    unit: data.unit,
    currency: data.currency,
    currentPrice: data.current_price,
    priceSource: data.price_source,
    historicalPrices: (data.historical_prices ?? []).map((p) => ({
      monthsAgo: p.months_ago,
      price: p.price,
    })),
    recommendation: data.recommendation,
    reasoning: data.reasoning,
    confidence: data.confidence,
  }
}

// ---- Plant disease detection from images (Tier 2) -------------------------

export async function detectDisease({ imageFile, cropHint, sessionId }) {
  const formData = new FormData()
  formData.append('image', imageFile)
  if (cropHint) formData.append('crop_hint', cropHint)
  if (sessionId) formData.append('session_id', sessionId)

  const res = await fetch(`${BASE_URL}/disease-detection`, { method: 'POST', body: formData })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = body?.detail
    throw new Error(`Request to /disease-detection failed: ${detail ?? `${res.status} ${res.statusText}`}`)
  }
  const data = await res.json()
  return {
    cropGuess: data.crop_guess,
    diseaseName: data.disease_name,
    isKnownInKnowledgeBase: data.is_known_in_knowledge_base,
    confidence: data.confidence,
    symptomsObserved: data.symptoms_observed,
    prevention: data.prevention,
    treatment: data.treatment,
    estimatedCostBDT: data.estimated_cost_bdt,
    source: data.source,
    disclaimer: data.disclaimer,
  }
}

// ---- Voice input transcription (Tier 2, OpenAI Whisper) -------------------

export async function transcribeAudio(audioBlob, language) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  if (language) formData.append('language', language)

  const res = await fetch(`${BASE_URL}/transcribe`, { method: 'POST', body: formData })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = body?.detail
    throw new Error(`Request to /transcribe failed: ${detail ?? `${res.status} ${res.statusText}`}`)
  }
  const data = await res.json()
  return data.text
}

// ---- Agent trace ----

const TOOL_LABELS = {
  weather: 'Weather API',
  rag_search: 'RAG Search',
  financial_calculator: 'Financial Calculator',
  fertilizer_scheduler: 'Fertilizer Scheduler',
  irrigation_scheduler: 'Irrigation Scheduler',
  pest_risk_assessor: 'Pest Risk Assessor',
  scenario_simulator: 'Scenario Simulator',
  marketplace: 'Marketplace',
}

function mapTrace(trace) {
  return (trace ?? []).map((t, i) => ({
    id: `trace_${i}_${t.tool_name}`,
    toolName: TOOL_LABELS[t.tool_name] ?? t.tool_name,
    input: t.input,
    output: t.output,
    status: t.status,
    timestamp: new Date().toISOString(),
    durationMs: null,
  }))
}

// ---- Proactive alerts: backend sends plain strings, UI wants rich objects ----

function mapAlerts(alerts) {
  return (alerts ?? []).map((text, i) => {
    const lower = text.toLowerCase()
    const severity = lower.includes('heavy rain') || lower.includes('high temperature') ? 'warning' : 'info'
    let relatedStage = null
    if (lower.includes('fertiliz')) relatedStage = 'Fertilizer'
    else if (lower.includes('irrigat')) relatedStage = 'Irrigation'
    else if (lower.includes('land preparation') || lower.includes('sowing')) relatedStage = 'Land Preparation'

    const firstSentence = text.split('. ')[0]
    return {
      id: `alert_${i}_${Date.now()}`,
      severity,
      title: firstSentence.endsWith('.') ? firstSentence : `${firstSentence}.`,
      message: text,
      reasoning: text,
      relatedStage,
      createdAt: new Date().toISOString(),
    }
  })
}

// ---- Weather ----

const WEEKDAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function conditionFromRainfall(mm) {
  if (mm >= 10) return 'Rain'
  if (mm > 0) return 'Cloudy'
  return 'Sunny'
}

function mapWeather(weather) {
  if (!weather) return null
  return {
    location: weather.location,
    current: {
      tempC: weather.temperature,
      condition: conditionFromRainfall(weather.rainfall),
      humidityPercent: weather.humidity,
      rainfallMm24h: weather.rainfall,
    },
    forecast: (weather.forecast ?? []).map((day) => {
      const d = new Date(day.date)
      return {
        day: Number.isNaN(d.getTime()) ? day.date : WEEKDAY_NAMES[d.getDay()],
        date: day.date,
        tempC: day.temperature_max,
        condition: conditionFromRainfall(day.precipitation_mm),
        rainfallMm: day.precipitation_mm,
      }
    }),
  }
}

// ---- Reply message ----

function mapReplyMessage(replyText) {
  return {
    id: `msg_${Date.now()}`,
    role: 'assistant',
    content: replyText,
    timestamp: new Date().toISOString(),
  }
}

// ---- Public API (same signatures api/index.js already expects) ------------

export async function sendChatMessage(text, farmerProfile, language = 'en') {
  const body = {
    message: text,
    session_id: getStoredSessionId() ?? undefined,
    farmer_key: getFarmerKey(farmerProfile),
    profile: toBackendProfile(farmerProfile),
    language,
  }

  const data = await request('/chat', { method: 'POST', body: JSON.stringify(body) })
  storeSessionId(data.session_id)

  return {
    sessionId: data.session_id,
    reply: mapReplyMessage(data.reply),
    profile: fromBackendProfile(data.farm_profile, farmerProfile),
    recommendations: mapRecommendations(data.recommendations),
    timeline: mapTimeline(data.season_plan),
    financials: mapFinancials(data.financial_summary),
    fertilizerSchedule: mapFertilizerSchedule(data.fertilizer_schedule),
    irrigationSchedule: mapIrrigationSchedule(data.irrigation_schedule),
    pestRisks: mapPestRisks(data.pest_risks),
    marketplaceOffers: mapMarketplaceOffers(data.marketplace_offers),
    trace: mapTrace(data.trace),
    alerts: mapAlerts(data.alerts),
    weather: mapWeather(data.weather),
  }
}

export async function fetchFarmerProfile() {
  const sessionId = getStoredSessionId()
  if (!sessionId) return null
  const data = await request(`/history?session_id=${encodeURIComponent(sessionId)}`)
  return fromBackendProfile(data.farm_profile)
}

export async function updateFarmerProfile(partial) {
  // The backend only accepts profile updates bundled with a /chat turn (there's
  // no standalone PATCH endpoint) — this resolves locally so profile-edit forms
  // still work instantly, and the values are sent on the next sendChatMessage call.
  return partial
}

// ---- Chat sidebar: list of this farmer's previous conversations ----------

export async function fetchSessionList(farmerKey) {
  if (!farmerKey) return []
  const rows = await request(`/sessions?farmer_key=${encodeURIComponent(farmerKey)}`)
  return rows.map((s) => ({
    sessionId: s.session_id,
    preview: s.preview || 'New conversation',
    updatedAt: s.updated_at,
  }))
}

// ---- Session restore: rebuild chat/profile/plan from the backend's own
// record of the session, rather than relying only on the browser's local
// cache — so a session genuinely survives closing the tab, clearing site
// data (as long as the session id itself is remembered), or opening on
// another device with the same session id. ------------------------------

export async function fetchSessionHistory(sessionId, priorFrontendProfile) {
  const data = await request(`/history?session_id=${encodeURIComponent(sessionId)}`)

  const messages = (data.messages ?? []).map((m, i) => ({
    id: `hist_${i}_${m.created_at}`,
    role: m.role,
    content: m.content,
    timestamp: m.created_at,
  }))

  const latestPlan = (data.season_plans ?? []).at(-1)
  const latestFinance = (data.financial_projections ?? []).at(-1)

  return {
    messages,
    profile: fromBackendProfile(data.farm_profile, priorFrontendProfile),
    timeline: latestPlan ? mapTimeline(latestPlan) : [],
    financials: latestFinance ? mapFinancials(latestFinance) : null,
  }
}

export async function fetchAgentTrace(sessionId) {
  const id = sessionId ?? getStoredSessionId()
  if (!id) return []
  const data = await request(`/history?session_id=${encodeURIComponent(id)}`)
  return (data.tool_trace ?? []).map((t, i) => ({
    id: `trace_${i}_${t.tool_name}`,
    toolName: TOOL_LABELS[t.tool_name] ?? t.tool_name,
    input: t.input_json,
    output: t.output_json,
    status: t.status,
    timestamp: t.created_at,
    durationMs: t.latency_ms != null ? Math.round(t.latency_ms) : null,
  }))
}
