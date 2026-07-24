import { createContext } from 'react'
import { mockWelcomeMessage } from '../api/mocks/chatConversation.mock.js'
import { loadState, STORAGE_KEY } from '../lib/storage.js'

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
  chat: {
    messages: [mockWelcomeMessage],
    isAgentTyping: false,
  },
  recommendations: [],
  timeline: [],
  financials: null,
  agentTrace: [],
  alerts: [],
  weather: null,
  ui: {
    activeSection: 'dashboard',
    activeProfileTab: 'personal',
    isSidebarOpen: false,
  },
}

const PERSISTED_KEYS = [
  'farmerProfile',
  'recommendations',
  'timeline',
  'financials',
  'agentTrace',
  'alerts',
  'weather',
]

export function pickPersistedFields(state) {
  const picked = {}
  for (const key of PERSISTED_KEYS) {
    picked[key] = state[key]
  }
  picked.chat = { messages: state.chat.messages }
  picked.ui = { activeSection: state.ui.activeSection }
  return picked
}

export function buildInitialState() {
  const stored = loadState(STORAGE_KEY, {})

  return {
    ...initialState,
    ...stored,
    farmerProfile: { ...initialState.farmerProfile, ...stored.farmerProfile },
    chat: {
      messages: stored.chat?.messages?.length ? stored.chat.messages : initialState.chat.messages,
      isAgentTyping: false,
    },
    ui: {
      ...initialState.ui,
      activeSection: stored.ui?.activeSection ?? initialState.ui.activeSection,
      isSidebarOpen: false,
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
    case 'RESET_ALL':
      return {
        ...initialState,
        chat: { messages: [mockWelcomeMessage], isAgentTyping: false },
      }
    default:
      return state
  }
}

export const AppStateContext = createContext(null)
