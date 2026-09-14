/** Preserve the official classifier label when asking for grounded guidance. */
export function buildDiseaseAssistantPayload(result) {
  const label = result.raw_label || result.class_name;
  if (typeof label !== 'string' || !label.includes('___')) {
    throw new Error('The detection result is missing its official class label. Please analyse the image again.');
  }

  const payload = {
    disease_label: label,
    confidence: result.confidence,
    crop: result.crop,
  };
  if (result.assessment) payload.assessment = result.assessment;
  if (result.weather) payload.weather = result.weather;
  return payload;
}
