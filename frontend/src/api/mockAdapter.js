import { mockFarmerProfile } from './mocks/farmerProfile.mock.js'
import { mockCropRecommendations } from './mocks/cropRecommendations.mock.js'
import { mockSeasonTimeline } from './mocks/seasonTimeline.mock.js'
import { mockFinancials } from './mocks/financials.mock.js'
import { mockAgentTrace } from './mocks/agentTrace.mock.js'
import { mockWeatherAlerts } from './mocks/weatherAlerts.mock.js'
import { mockWeatherSnapshot } from './mocks/weather.mock.js'
import { buildMockReply } from './mocks/chatConversation.mock.js'

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function randomLatency(min = 400, max = 1200) {
  return Math.floor(Math.random() * (max - min)) + min
}

function withoutEmptyValues(profile = {}) {
  return Object.fromEntries(Object.entries(profile).filter(([, value]) => value !== '' && value != null))
}

export async function sendChatMessage(_text, farmerProfile) {
  await sleep(randomLatency())
  const mergedProfile = { ...mockFarmerProfile, ...withoutEmptyValues(farmerProfile) }
  return {
    reply: buildMockReply(),
    profile: mergedProfile,
    recommendations: mockCropRecommendations,
    timeline: mockSeasonTimeline,
    financials: mockFinancials,
    trace: mockAgentTrace,
    alerts: mockWeatherAlerts,
    weather: mockWeatherSnapshot,
  }
}

export async function fetchFarmerProfile() {
  await sleep(200)
  return mockFarmerProfile
}

export async function updateFarmerProfile(partial) {
  await sleep(150)
  return { ...mockFarmerProfile, ...partial }
}

export async function fetchAgentTrace() {
  await sleep(150)
  return mockAgentTrace
}
