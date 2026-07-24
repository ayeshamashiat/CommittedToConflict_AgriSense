export const mockWeatherAlerts = [
  {
    id: 'alert_1',
    severity: 'warning',
    title: 'Heavy rain forecast in 4 days',
    message: 'Delay the nitrogen application by 4 days to cut runoff loss.',
    reasoning:
      '18mm of rain is forecast for Rangpur on Nov 29. Applying urea before then would wash a significant share of nitrogen off your loamy topsoil before Boro rice at the vegetative stage can absorb it.',
    relatedStage: 'Fertilizer',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'alert_2',
    severity: 'info',
    title: 'Dry spell continues through next week',
    message: 'Bring forward your next irrigation cycle by 2 days.',
    reasoning:
      'No rainfall is forecast for the next 7 days and standing water in your paddy has dropped below the 2cm target — irrigate early to avoid stressing Boro rice at the vegetative stage.',
    relatedStage: 'Irrigation',
    createdAt: new Date().toISOString(),
  },
]
