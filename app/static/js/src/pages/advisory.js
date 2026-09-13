/**
 * Advisory Dashboard Page - Modules A-D
 */

import API from '../core/api.js';
import UI from '../components/ui.js';
import DOM from '../utils/dom.js';

// Initialize advisory page
document.addEventListener('DOMContentLoaded', () => {
  console.log('Advisory dashboard loaded');
  
  initModuleA(); // Crop recommendation
  initModuleB(); // Irrigation advisory
  initModuleC(); // Weather advisory
  initModuleD(); // Sustainability scoring
});

/**
 * Get number from form
 * @param {HTMLFormElement} form
 * @param {string} name
 * @returns {number}
 */
function getNumber(form, name) {
  return Number(new FormData(form).get(name));
}

/**
 * Display module result
 * @param {Object} data - API response
 * @param {HTMLElement} container - Output container
 */
function displayResult(data, container) {
  const isSuccess = API.isSuccess(data);
  
  container.className = `output output--${isSuccess ? 'success' : 'error'}`;
  container.innerHTML = '';
  
  // Status header
  const status = document.createElement('div');
  status.className = 'output__status';
  status.textContent = data.status || 'UNKNOWN';
  
  // Summary
  const summary = createResultSummary(data);
  
  // Technical details
  const disclosure = document.createElement('details');
  const disclosureTitle = document.createElement('summary');
  disclosureTitle.textContent = 'Technical response';
  const details = document.createElement('pre');
  details.className = 'text-xs bg-gray-800 text-gray-100 p-4 rounded overflow-auto max-h-96';
  details.textContent = JSON.stringify(data, null, 2);
  disclosure.append(disclosureTitle, details);
  
  container.append(status, summary, disclosure);
}

/**
 * Create result summary based on module
 * @param {Object} data - API response
 * @returns {HTMLElement}
 */
function createResultSummary(data) {
  const summary = document.createElement('div');
  summary.className = 'output__summary';
  
  const title = document.createElement('h3');
  title.className = 'text-xl font-bold text-gray-900 mb-3';
  
  const body = document.createElement('div');
  body.className = 'text-gray-700';
  
  const result = data.result;
  
  if (!result) {
    title.textContent = 'Result withheld';
    const reason = data.reasons?.[0]?.message || 'The request could not be completed.';
    body.textContent = reason;
  } else if (data.module === 'A') {
    // Crop Recommendation
    title.textContent = 'Top crop candidates';
    const list = document.createElement('ol');
    list.className = 'list-decimal list-inside space-y-2';
    result.candidates.forEach((candidate) => {
      const item = document.createElement('li');
      item.className = 'text-gray-800';
      item.innerHTML = `<strong>${candidate.crop}</strong> 
        <span class="text-gray-600">· ${(candidate.model_score * 100).toFixed(1)}% model score</span>`;
      list.append(item);
    });
    body.append(list);
  } else if (data.module === 'B') {
    // Irrigation Advisory
    title.textContent = result.action === 'IRRIGATE' ? 'Irrigation indicated' : 'No irrigation needed';
    const desc = document.createElement('p');
    desc.textContent = result.action === 'IRRIGATE'
      ? `Apply ${result.gross_depth_mm} mm gross depth, approximately ${result.volume_m3} m³ over ${result.target_area_ha} ha.`
      : `Projected depletion is ${result.projected_depletion_mm} mm, below the ${result.readily_available_water_mm} mm threshold. No irrigation needed.`;
    body.append(desc);
  } else if (data.module === 'C') {
    // Weather Advisory
    title.textContent = result.alerts.length 
      ? `${result.alerts.length} condition${result.alerts.length === 1 ? '' : 's'} flagged` 
      : 'No alerts triggered';
    const list = document.createElement('ul');
    list.className = 'list-disc list-inside space-y-2';
    result.alerts.forEach((alert) => {
      const item = document.createElement('li');
      item.className = 'text-gray-800';
      item.innerHTML = `<strong>${alert.flag.replaceAll('_', ' ')}</strong> 
        <span class="text-gray-600">— ${alert.action}</span>`;
      list.append(item);
    });
    if (result.alerts.length > 0) {
      body.append(list);
    } else {
      body.textContent = 'Weather conditions are within normal parameters for the next 24 hours.';
    }
  } else if (data.module === 'D') {
    // Sustainability Scoring
    title.textContent = `Sustainability Score: ${result.score.toFixed(2)} / 100`;
    const desc = document.createElement('p');
    desc.textContent = result.yield_gate_applied
      ? 'The resource score was capped because yield retention fell below 95%. Ensure crop health is maintained.'
      : `Yield retention: ${(result.yield_retention_ratio * 100).toFixed(1)}%. Formula version ${result.formula_version}.`;
    body.append(desc);
    
    // Add breakdown if available
    if (result.component_scores) {
      const breakdown = document.createElement('div');
      breakdown.className = 'mt-3 grid grid-cols-3 gap-3';
      Object.entries(result.component_scores).forEach(([key, value]) => {
        const card = document.createElement('div');
        card.className = 'p-3 bg-gray-50 rounded border border-gray-200';
        card.innerHTML = `
          <div class="text-xs text-gray-600 mb-1">${key}</div>
          <div class="text-lg font-bold text-gray-900">${value.toFixed(1)}</div>
        `;
        breakdown.append(card);
      });
      body.append(breakdown);
    }
  }
  
  summary.append(title, body);
  return summary;
}

/**
 * Initialize Module A - Crop Recommendation
 */
function initModuleA() {
  const form = DOM.byId('crop-form');
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const output = DOM.byId('crop-output');
    if (!output) return;
    
    UI.showLoading(output, 'Analyzing soil and climate data...');
    
    const payload = API.createEnvelope('A', 'dataset_benchmark', {
      mode: 'source_dataset_classifier',
      dataset_id: 'atharvaingle/crop-recommendation-dataset',
      dataset_version: 1,
      dataset_sha256: '54a5a6e5408668e668667efc50de2fc867c1b875e0431b4f54dd331b0a109a4e',
      features: {
        N: getNumber(form, 'N'),
        P: getNumber(form, 'P'),
        K: getNumber(form, 'K'),
        temperature: getNumber(form, 'temperature'),
        humidity: getNumber(form, 'humidity'),
        ph: getNumber(form, 'ph'),
        rainfall: getNumber(form, 'rainfall'),
      },
    });
    
    try {
      const data = await API.recommendCrops(payload);
      displayResult(data, output);
    } catch (error) {
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module A error:', error);
    }
  });
}

/**
 * Initialize Module B - Irrigation Advisory
 */
function initModuleB() {
  const form = DOM.byId('irrigation-form');
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const output = DOM.byId('irrigation-output');
    if (!output) return;
    
    UI.showLoading(output, 'Calculating water balance...');
    
    const area = getNumber(form, 'area');
    const payload = API.createEnvelope('B', 'simulation', {
      mode: 'soil_water_balance',
      soil_moisture: { ...API.createMeasurement(getNumber(form, 'moisture'), 'm3/m3'), calibration_reference: 'dashboard-simulation-calibration' },
      soil_profile: {
        field_capacity: API.createMeasurement(getNumber(form, 'fieldCapacity'), 'm3/m3'),
        wilting_point: API.createMeasurement(getNumber(form, 'wiltingPoint'), 'm3/m3')
      },
      root_depth: API.createMeasurement(getNumber(form, 'rootDepth'), 'm'),
      allowable_depletion_fraction: API.createMeasurement(getNumber(form, 'depletion'), 'fraction'),
      crop_coefficient: API.createMeasurement(getNumber(form, 'cropCoefficient'), 'fraction'),
      weather: {
        et0_24h: API.createMeasurement(getNumber(form, 'et0'), 'mm', 'forecast'),
        precipitation_24h: API.createMeasurement(getNumber(form, 'rain'), 'mm', 'forecast')
      },
      recent_water_events: {
        effective_water_mm: API.createMeasurement(getNumber(form, 'recentWater'), 'mm')
      },
      application_efficiency: API.createMeasurement(getNumber(form, 'efficiency'), 'fraction'),
      target_area_ha: area,
    }, 
    { field_id: 'dashboard-demo', area_ha: area },
    { crop: 'tomato', growth_stage: 'vegetative' });
    
    try {
      const data = await API.adviseIrrigation(payload);
      displayResult(data, output);
    } catch (error) {
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module B error:', error);
    }
  });
}

/**
 * Initialize Module C - Weather Advisory
 */
function initModuleC() {
  const form = DOM.byId('weather-form');
  const demoBtn = DOM.byId('weather-demo');
  
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await runWeatherAdvisory(false);
  });
  
  if (demoBtn) {
    demoBtn.addEventListener('click', async () => {
      if (!form.reportValidity()) return;
      await runWeatherAdvisory(true);
    });
  }
}

/**
 * Run weather advisory
 * @param {boolean} isDemo - Whether to run demo mode
 */
async function runWeatherAdvisory(isDemo) {
  const form = DOM.byId('weather-form');
  const output = DOM.byId('weather-output');
  
  if (!form || !output) return;
  
  UI.showLoading(output, 'Fetching weather forecast...');
  
  const farm = {
    field_id: isDemo ? 'dashboard-demo' : 'dashboard-location',
    location: {
      latitude: getNumber(form, 'latitude'),
      longitude: getNumber(form, 'longitude')
    },
    area_ha: 1
  };
  
  const payload = API.createEnvelope('C', isDemo ? 'simulation' : 'farm_advisory', {
    mode: isDemo ? 'demo_forecast' : 'forecast_advisory',
    horizon_hours: 24
  }, farm);
  
  try {
    const data = await API.adviseWeather(payload);
    displayResult(data, output);
  } catch (error) {
    UI.showError(output, 'Request failed. Please try again.');
    console.error('Module C error:', error);
  }
}

/**
 * Initialize Module D - Sustainability Scoring
 */
function initModuleD() {
  const form = DOM.byId('sustainability-form');
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const output = DOM.byId('sustainability-output');
    if (!output) return;
    
    UI.showLoading(output, 'Computing sustainability score...');
    
    const createRecord = (prefix) => ({
      crop: 'tomato',
      location: 'Dashboard simulated plot',
      basis: 'whole_crop_cycle',
      data_kind: 'simulated',
      area_ha: 1,
      period_start_utc: '2026-01-01T00:00:00Z',
      period_end_utc: '2026-05-01T00:00:00Z',
      water: { ...API.createMeasurement(getNumber(form, `${prefix}Water`), 'm3'), accounting_scope: 'All irrigation water applied at plot inlet' },
      electricity: { ...API.createMeasurement(getNumber(form, `${prefix}Electricity`), 'kWh'), accounting_scope: 'All irrigation pumping electricity; no other pumping fuels' },
      nitrogen: { ...API.createMeasurement(getNumber(form, `${prefix}Nitrogen`), 'kg_N'), accounting_scope: 'Total nitrogen nutrient from mineral and organic fertilizers' },
      harvest: { ...API.createMeasurement(getNumber(form, `${prefix}Harvest`), 'kg'), accounting_scope: 'Whole-cycle harvested output' },
    });
    
    const payload = API.createEnvelope('D', 'simulation', {
      mode: 'resource_comparison',
      baseline: createRecord('baseline'),
      current: createRecord('current'),
      comparison_evidence: {
        kind: 'assumed',
        note: 'Dashboard simulation assumes the same crop, plot, period, and accounting scope.',
        references: []
      },
    });
    
    try {
      const data = await API.scoreSustainability(payload);
      displayResult(data, output);
    } catch (error) {
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module D error:', error);
    }
  });
}

export { initModuleA, initModuleB, initModuleC, initModuleD };
