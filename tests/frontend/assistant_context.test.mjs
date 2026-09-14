import assert from 'node:assert/strict';
import test from 'node:test';
import { buildDiseaseAssistantPayload } from '../../app/static/js/src/utils/assistant-context.mjs';

test('uses the API raw label rather than the readable disease name', () => {
  assert.deepEqual(buildDiseaseAssistantPayload({
    raw_label: 'Tomato___Early_blight',
    disease: 'Early blight',
    class_name: 'Potato___Early_blight',
    confidence: 0.91,
    crop: 'Tomato',
  }), {
    disease_label: 'Tomato___Early_blight',
    confidence: 0.91,
    crop: 'Tomato',
  });
});

test('preserves punctuation in official labels', () => {
  const label = 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot';
  assert.equal(buildDiseaseAssistantPayload({ raw_label: label }).disease_label, label);
});

test('supports the legacy class_name field when it contains an official label', () => {
  assert.equal(buildDiseaseAssistantPayload({
    class_name: 'Tomato___healthy',
    disease: 'healthy',
  }).disease_label, 'Tomato___healthy');
});

test('does not guess a label from a display name or an incomplete result', () => {
  for (const result of [{}, { disease: 'Early blight' }, { raw_label: 'Early blight' }]) {
    assert.throws(() => buildDiseaseAssistantPayload(result), /official class label/);
  }
});
