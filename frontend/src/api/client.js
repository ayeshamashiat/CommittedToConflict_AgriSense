const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function sendChatMessage(text, farmerProfile) {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: text, farmer_profile: farmerProfile }),
  })
}

export async function fetchFarmerProfile() {
  return request('/api/farmer-profile')
}

export async function updateFarmerProfile(partial) {
  return request('/api/farmer-profile', {
    method: 'PATCH',
    body: JSON.stringify(partial),
  })
}

export async function fetchAgentTrace(sessionId) {
  return request(`/api/agent-trace/${sessionId}`)
}
