export const mockCropRecommendations = [
  {
    id: 'crop_1',
    cropName: 'Boro Rice',
    suitability: 'High',
    riskLevel: 'Low',
    waterNeed: 'High',
    estimatedProfitBDT: 42000,
    reasoning:
      'Well-suited to loamy soil and medium water availability during Rabi season; strong historical yield in Rangpur district with forecast rainfall covering irrigation gaps.',
  },
  {
    id: 'crop_2',
    cropName: 'Wheat',
    suitability: 'Medium',
    riskLevel: 'Low',
    waterNeed: 'Low',
    estimatedProfitBDT: 28500,
    reasoning:
      'Low water need fits your medium water availability comfortably, but Rangpur soil moisture in Rabi season caps yield below rice-level returns.',
  },
  {
    id: 'crop_3',
    cropName: 'Potato',
    suitability: 'Medium',
    riskLevel: 'Medium',
    waterNeed: 'Medium',
    estimatedProfitBDT: 51000,
    reasoning:
      'Highest profit potential of the three, but higher fertilizer cost and blight risk in cool, humid Rabi weeks raise the risk profile.',
  },
]
