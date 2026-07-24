export const mockWelcomeMessage = {
  id: 'msg_welcome',
  role: 'assistant',
  content:
    "Hi! I'm AgriSense AI. Tell me about your farm — location, size, budget, soil type, water availability, and target season — and I'll build you a costed, weather-aware season plan.",
  timestamp: new Date().toISOString(),
}

export function buildMockReply() {
  return {
    id: `msg_${Date.now()}`,
    role: 'assistant',
    content:
      `Based on your profile in Rangpur (2.5 acres, loamy soil, medium water availability, Rabi season) and the latest weather data, ` +
      `I've ranked 3 crops, built a season timeline, and costed out the plan. Boro Rice comes out on top — check the tabs below for the full breakdown, and the trace panel for exactly which tools I called to get there.`,
    timestamp: new Date().toISOString(),
  }
}
