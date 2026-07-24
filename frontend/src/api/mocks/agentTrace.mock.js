export const mockAgentTrace = [
  {
    id: 'trace_1',
    toolName: 'Weather API',
    input: { location: 'Rangpur, Bangladesh', season: 'Rabi' },
    output: { avgRainfallMm: 120, avgTempC: 22, forecastNote: 'Dry spell expected next 10 days' },
    status: 'success',
    timestamp: '2026-07-24T10:15:02Z',
    durationMs: 340,
  },
  {
    id: 'trace_2',
    toolName: 'RAG Search',
    input: { query: 'rice fertilizer schedule loamy soil Rabi season Rangpur' },
    output: {
      retrievedDocs: [
        'BARI Rice Cultivation Guide 2024 — Section 4.2 Fertilizer Management',
        'DAE Rangpur District Soil & Crop Zoning Report',
      ],
    },
    status: 'success',
    timestamp: '2026-07-24T10:15:02Z',
    durationMs: 610,
  },
  {
    id: 'trace_3',
    toolName: 'Financial Calculator',
    input: { cropName: 'Boro Rice', farmSizeAcres: 2.5, budgetBDT: 50000 },
    output: { totalCostBDT: 37500, expectedRevenueBDT: 79500, netProfitBDT: 42000, roiPercent: 112.0 },
    status: 'success',
    timestamp: '2026-07-24T10:15:03Z',
    durationMs: 180,
  },
  {
    id: 'trace_4',
    toolName: 'Final Recommendation',
    input: { candidateCrops: ['Boro Rice', 'Wheat', 'Potato'] },
    output: { rankedTop: 'Boro Rice', reason: 'Highest suitability with lowest risk given forecast rainfall gap' },
    status: 'success',
    timestamp: '2026-07-24T10:15:03Z',
    durationMs: 90,
  },
]
