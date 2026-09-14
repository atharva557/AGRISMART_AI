import assert from 'node:assert/strict';
import test from 'node:test';
import { weatherContext, scanLocation } from '../../app/static/js/src/utils/diagnosis-flow.mjs';
import { buildDiseaseAssistantPayload } from '../../app/static/js/src/utils/assistant-context.mjs';

test('live weather never substitutes example coordinates for missing input', () => {
  assert.throws(() => scanLocation('live', '', ''), /coordinates/);
  assert.throws(() => scanLocation('live', 95, 73), /latitude/);
  assert.deepEqual(scanLocation('live', '0', '0'), { latitude: 0, longitude: 0 });
  assert.equal(scanLocation('none', '', ''), null);
});

test('failed weather is absent and successful weather retains evidence', () => {
  assert.equal(weatherContext({ status: 'DATA_UNAVAILABLE' }), null);
  const weather = weatherContext({ status: 'SIMULATED', result: {
    fetched_at_utc: '2026-09-15T00:00:00Z', valid_from_utc: 'start', valid_to_utc: 'end',
    alerts: [{ action: 'Scout foliage' }], requested_location: { latitude: 1, longitude: 2 },
  }, sources: [{ title: 'Example fixture' }] });
  assert.equal(weather.status, 'SIMULATED');
  assert.equal(weather.source, 'Example fixture');
  assert.equal(weather.valid_to_utc, 'end');
  const assessment = { state: 'CROP_MISMATCH', withheld: true };
  const payload = buildDiseaseAssistantPayload({ raw_label: 'Tomato___healthy', weather, assessment });
  assert.deepEqual(payload.weather, weather);
  assert.deepEqual(payload.assessment, assessment);
});
