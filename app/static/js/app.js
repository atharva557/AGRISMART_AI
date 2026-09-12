const byId = (id) => document.getElementById(id);
const number = (form, name) => Number(new FormData(form).get(name));

function envelope(module, purpose, inputs, farm = null, cropContext = null) {
  return {
    contract_version: '0.1.0', request_id: `${module}-${Date.now()}`, module, purpose,
    as_of_utc: new Date().toISOString(), farm, crop_context: cropContext, inputs,
  };
}

function evidence(kind = 'assumed') {
  return {
    kind, source: 'AgriSmart dashboard simulation', method: 'User-entered dashboard value',
    observed_at_utc: new Date().toISOString(), period_start_utc: null, period_end_utc: null,
    reference_id: kind === 'assumed' ? 'dashboard-simulation' : null,
  };
}

const measure = (value, unit, kind = 'assumed') => ({ value, unit, evidence: evidence(kind) });

function resultSummary(data) {
  const summary = document.createElement('div');
  summary.className = 'output__summary';
  const title = document.createElement('h3');
  const body = document.createElement('div');
  const result = data.result;

  if (!result) {
    title.textContent = 'Result withheld';
    const reason = data.reasons?.[0]?.message || 'The request could not be completed.';
    body.textContent = reason;
  } else if (data.module === 'A') {
    title.textContent = 'Top crop labels';
    const list = document.createElement('ol');
    result.candidates.forEach((candidate) => {
      const item = document.createElement('li');
      item.textContent = `${candidate.crop} · ${(candidate.model_score * 100).toFixed(1)} model score`;
      list.append(item);
    });
    body.append(list);
  } else if (data.module === 'B') {
    title.textContent = result.action === 'IRRIGATE' ? 'Irrigation indicated' : 'Wait and monitor';
    body.textContent = result.action === 'IRRIGATE'
      ? `${result.gross_depth_mm} mm gross depth, approximately ${result.volume_m3} m³ over ${result.target_area_ha} ha.`
      : `Projected depletion is ${result.projected_depletion_mm} mm, below the ${result.readily_available_water_mm} mm threshold.`;
  } else if (data.module === 'C') {
    title.textContent = result.alerts.length ? `${result.alerts.length} condition${result.alerts.length === 1 ? '' : 's'} flagged` : 'No configured alert triggered';
    const list = document.createElement('ul');
    result.alerts.forEach((alert) => {
      const item = document.createElement('li');
      item.textContent = `${alert.flag.replaceAll('_', ' ')} — ${alert.action}`;
      list.append(item);
    });
    body.append(list);
  } else if (data.module === 'D') {
    title.textContent = `${result.score.toFixed(2)} / 100`;
    body.textContent = result.yield_gate_applied
      ? 'The resource score was capped because yield retention fell below 95%.'
      : `Yield retention: ${(result.yield_retention_ratio * 100).toFixed(1)}%. Formula version ${result.formula_version}.`;
  }
  summary.append(title, body);
  return summary;
}

async function postJson(path, payload, outputId) {
  const target = byId(outputId);
  target.className = 'output output--loading';
  target.textContent = 'Working…';
  try {
    const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await response.json();
    target.className = `output output--${response.ok ? 'success' : 'error'}`;
    target.replaceChildren();
    const status = document.createElement('div');
    status.className = 'output__status';
    status.textContent = data.status || `HTTP ${response.status}`;
    const summary = resultSummary(data);
    const disclosure = document.createElement('details');
    const disclosureTitle = document.createElement('summary');
    disclosureTitle.textContent = 'Technical response';
    const details = document.createElement('pre');
    details.textContent = JSON.stringify(data, null, 2);
    disclosure.append(disclosureTitle, details);
    target.append(status, summary, disclosure);
  } catch (error) {
    target.className = 'output output--error';
    target.textContent = `Request failed: ${error.message}`;
  }
}

async function checkHealth() {
  const target = byId('connection');
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    if (!response.ok || data.status !== 'ok') throw new Error('Unexpected response');
    target.textContent = 'Backend connected · A–D API routes ready';
    target.classList.add('connection--ok');
  } catch {
    target.textContent = 'Backend unavailable · start the Flask server to run modules';
  }
}

byId('crop-form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  postJson('/api/crops/recommend', envelope('A', 'dataset_benchmark', {
    mode: 'source_dataset_classifier', dataset_id: 'atharvaingle/crop-recommendation-dataset', dataset_version: 1,
    dataset_sha256: '54a5a6e5408668e668667efc50de2fc867c1b875e0431b4f54dd331b0a109a4e',
    features: Object.fromEntries(['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'].map((name) => [name, number(form, name)])),
  }), 'crop-output');
});

byId('irrigation-form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const area = number(form, 'area');
  postJson('/api/irrigation/advise', envelope('B', 'simulation', {
    mode: 'soil_water_balance',
    soil_moisture: { ...measure(number(form, 'moisture'), 'm3/m3'), calibration_reference: 'dashboard-simulation-calibration' },
    soil_profile: { field_capacity: measure(number(form, 'fieldCapacity'), 'm3/m3'), wilting_point: measure(number(form, 'wiltingPoint'), 'm3/m3') },
    root_depth: measure(number(form, 'rootDepth'), 'm'), allowable_depletion_fraction: measure(number(form, 'depletion'), 'fraction'),
    crop_coefficient: measure(number(form, 'cropCoefficient'), 'fraction'),
    weather: { et0_24h: measure(number(form, 'et0'), 'mm', 'forecast'), precipitation_24h: measure(number(form, 'rain'), 'mm', 'forecast') },
    recent_water_events: { effective_water_mm: measure(number(form, 'recentWater'), 'mm') },
    application_efficiency: measure(number(form, 'efficiency'), 'fraction'), target_area_ha: area,
  }, { field_id: 'dashboard-demo', area_ha: area }, { crop: 'tomato', growth_stage: 'vegetative' }), 'irrigation-output');
});

byId('weather-form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const farm = { field_id: 'dashboard-location', location: { latitude: number(form, 'latitude'), longitude: number(form, 'longitude') }, area_ha: 1 };
  postJson('/api/weather/advise', envelope('C', 'farm_advisory', { mode: 'forecast_advisory', horizon_hours: 24 }, farm), 'weather-output');
});

byId('weather-demo')?.addEventListener('click', () => {
  const form = byId('weather-form');
  if (!form.reportValidity()) return;
  const farm = { field_id: 'dashboard-demo', location: { latitude: number(form, 'latitude'), longitude: number(form, 'longitude') }, area_ha: 1 };
  postJson('/api/weather/advise', envelope('C', 'simulation', { mode: 'demo_forecast', horizon_hours: 24 }, farm), 'weather-output');
});

function resource(value, unit, scope) { return { ...measure(value, unit), accounting_scope: scope }; }

byId('sustainability-form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const common = { crop: 'tomato', location: 'Dashboard simulated plot', basis: 'whole_crop_cycle', data_kind: 'simulated', area_ha: 1, period_start_utc: '2026-01-01T00:00:00Z', period_end_utc: '2026-05-01T00:00:00Z' };
  const record = (prefix) => ({
    ...common,
    water: resource(number(form, `${prefix}Water`), 'm3', 'All irrigation water applied at plot inlet'),
    electricity: resource(number(form, `${prefix}Electricity`), 'kWh', 'All irrigation pumping electricity; no other pumping fuels'),
    nitrogen: resource(number(form, `${prefix}Nitrogen`), 'kg_N', 'Total nitrogen nutrient from mineral and organic fertilizers'),
    harvest: resource(number(form, `${prefix}Harvest`), 'kg', 'Whole-cycle harvested output'),
  });
  postJson('/api/sustainability/score', envelope('D', 'simulation', {
    mode: 'resource_comparison', baseline: record('baseline'), current: record('current'),
    comparison_evidence: { kind: 'assumed', note: 'Dashboard simulation assumes the same crop, plot, period, and accounting scope.', references: [] },
  }), 'sustainability-output');
});

checkHealth();
