import { createContext } from 'react'
import { loadState, STORAGE_KEY } from '../lib/storage.js'
import { translate } from '../lib/i18n.js'

function buildWelcomeMessage(language = 'en') {
  return {
    id: 'msg_welcome',
    role: 'assistant',
    content: translate(language, 'welcomeMessage'),
    timestamp: new Date().toISOString(),
  }
}

export const initialState = {
  farmerProfile: {
    farmerName: '',
    phoneNumber: '',
    location: '',
    farmSizeAcres: null,
    budgetBDT: null,
    soilType: '',
    waterAvailability: '',
    season: '',
  },
  currentSessionId: null,
  chat: {
    messages: [buildWelcomeMessage('en')],
    isAgentTyping: false,
  },
  recommendations: [],
  timeline: [],
  financials: null,
  fertilizerSchedule: null,
  irrigationSchedule: null,
  pestRisks: null,
  marketplaceOffers: null,
  agentTrace: [],
  alerts: [],
  weather: null,
  ui: {
    activeSection: 'dashboard',
    activeProfileTab: 'personal',
    isSidebarOpen: false,
    language: 'en',
  },
}

// Deliberately excludes chat.messages and currentSessionId — every app open
// starts a brand new conversation (see AppStateContext's mount effect), so
// there is nothing to gain from persisting the previous conversation's
// messages locally. Past conversations are still reachable via the chat
// sidebar, which reads them from the backend by session id.
const PERSISTED_KEYS = [
  'farmerProfile',
  'recommendations',
  'timeline',
  'financials',
  'fertilizerSchedule',
  'irrigationSchedule',
  'pestRisks',
  'marketplaceOffers',
  'agentTrace',
  'alerts',
  'weather',
]

export function pickPersistedFields(state) {
  const picked = {}
  for (const key of PERSISTED_KEYS) {
    picked[key] = state[key]
  }
  picked.ui = { activeSection: state.ui.activeSection, language: state.ui.language }
  return picked
}

export function buildInitialState() {
  const stored = loadState(STORAGE_KEY, {})
  const language = stored.ui?.language ?? initialState.ui.language

  return {
    ...initialState,
    ...stored,
    farmerProfile: { ...initialState.farmerProfile, ...stored.farmerProfile },
    currentSessionId: null,
    chat: { messages: [buildWelcomeMessage(language)], isAgentTyping: false },
    ui: {
      ...initialState.ui,
      activeSection: stored.ui?.activeSection ?? initialState.ui.activeSection,
      isSidebarOpen: false,
      language,
    },
  }
}

export function reducer(state, action) {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, chat: { ...state.chat, messages: [...state.chat.messages, action.payload] } }
    case 'SET_AGENT_TYPING':
      return { ...state, chat: { ...state.chat, isAgentTyping: action.payload } }
    case 'SET_PROFILE':
      return { ...state, farmerProfile: { ...state.farmerProfile, ...action.payload } }
    case 'SET_CURRENT_SESSION':
      return { ...state, currentSessionId: action.payload }
    case 'SWITCH_SESSION':
      // A farmer picked a past conversation from the chat sidebar — replace
      // (not merge) the conversation-scoped fields with that session's own
      // record. Only the last recommended crop's plan/financials are stored
      // server-side per session (not the full 3-crop comparison), so those
      // reset to empty rather than showing stale data from whatever was open
      // before.
      return {
        ...state,
        currentSessionId: action.payload.sessionId,
        farmerProfile: action.payload.profile ?? state.farmerProfile,
        chat: {
          messages: action.payload.messages.length ? action.payload.messages : [buildWelcomeMessage(state.ui.language)],
          isAgentTyping: false,
        },
        recommendations: [],
        timeline: action.payload.timeline,
        financials: action.payload.financials,
        fertilizerSchedule: null,
        irrigationSchedule: null,
        pestRisks: null,
        marketplaceOffers: null,
        alerts: [],
        weather: null,
        agentTrace: [],
      }
    case 'SET_PROFILE_FIELD':
      return {
        ...state,
        farmerProfile: { ...state.farmerProfile, [action.payload.field]: action.payload.value },
      }
    case 'SET_RECOMMENDATIONS':
      return { ...state, recommendations: action.payload }
    case 'SET_TIMELINE':
      return { ...state, timeline: action.payload }
    case 'SET_FINANCIALS':
      return { ...state, financials: action.payload }
    case 'SET_FERTILIZER_SCHEDULE':
      return { ...state, fertilizerSchedule: action.payload }
    case 'SET_IRRIGATION_SCHEDULE':
      return { ...state, irrigationSchedule: action.payload }
    case 'SET_PEST_RISKS':
      return { ...state, pestRisks: action.payload }
    case 'SET_MARKETPLACE_OFFERS':
      return { ...state, marketplaceOffers: action.payload }
    case 'SET_WEATHER':
      return { ...state, weather: action.payload }
    case 'APPEND_TRACE_EVENT':
      return { ...state, agentTrace: [...state.agentTrace, action.payload] }
    case 'RESET_TRACE':
      return { ...state, agentTrace: [] }
    case 'SET_ALERTS':
      return { ...state, alerts: action.payload }
    case 'DISMISS_ALERT':
      return { ...state, alerts: state.alerts.filter((alert) => alert.id !== action.payload) }
    case 'SET_SECTION':
      return { ...state, ui: { ...state.ui, activeSection: action.payload, isSidebarOpen: false } }
    case 'SET_PROFILE_TAB':
      return { ...state, ui: { ...state.ui, activeProfileTab: action.payload } }
    case 'TOGGLE_SIDEBAR':
      return { ...state, ui: { ...state.ui, isSidebarOpen: !state.ui.isSidebarOpen } }
    case 'SET_LANGUAGE':
      return { ...state, ui: { ...state.ui, language: action.payload } }
    case 'RESET_ALL':
      return {
        ...initialState,
        chat: { messages: [buildWelcomeMessage(state.ui.language)], isAgentTyping: false },
      }
    case 'START_NEW_CHAT':
      // A fresh conversation (new backend session_id, cleared by the caller
      // before dispatching this) but NOT a fresh farmer — farmerProfile stays
      // so the backend's farmer_key carry-forward has something to restore
      // into the new session, and so the profile page doesn't blank out.
      return {
        ...state,
        currentSessionId: null,
        chat: { messages: [buildWelcomeMessage(state.ui.language)], isAgentTyping: false },
        recommendations: [],
        timeline: [],
        financials: null,
        fertilizerSchedule: null,
        irrigationSchedule: null,
        pestRisks: null,
        marketplaceOffers: null,
        agentTrace: [],
        alerts: [],
        weather: null,
      }
    default:
      return state
  }
}

export const AppStateContext = createContext(null)
