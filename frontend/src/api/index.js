import * as mockAdapter from './mockAdapter.js'
import * as realClient from './client.js'

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

const impl = USE_MOCK ? mockAdapter : realClient

export const sendChatMessage = impl.sendChatMessage
export const fetchFarmerProfile = impl.fetchFarmerProfile
export const updateFarmerProfile = impl.updateFarmerProfile
export const fetchAgentTrace = impl.fetchAgentTrace
