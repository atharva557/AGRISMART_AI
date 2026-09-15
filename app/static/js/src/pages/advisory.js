/**
 * Advisory Dashboard Page - Modules A-D
 */

import API from '../core/api.js';
import UI from '../components/ui.js';
import DOM from '../utils/dom.js';
import LeafLoader from '../components/loader.js';

// Initialize advisory page
document.addEventListener('DOMContentLoaded', () => {
  console.log('Advisory dashboard loaded');
  
  initModuleA(); // Crop recommendation
  initModuleB(); // Irrigation advisory
  initModuleC(); // Weather advisory
  initModuleD(); // Sustainability scoring
  initModuleE(); // GenAI Conversational Agronomist (Module 6)
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
 * Uses CSS variables for Dark Mode compatibility — no hard-coded Tailwind colour classes.
 * @param {Object} data - API response
 * @returns {HTMLElement}
 */
function createResultSummary(data) {
  const summary = document.createElement('div');
  summary.className = 'output__summary';

  const title = document.createElement('h3');
  // CSS variable–based colour so it works in both Light and Dark
  title.style.cssText = 'font-size:1.15rem;font-weight:700;margin:0 0 0.75rem;color:var(--text-primary);';

  const body = document.createElement('div');
  body.style.color = 'var(--text-secondary)';

  const result = data.result;

  if (!result) {
    title.textContent = 'Result withheld';
    const reason = data.reasons?.[0]?.message || 'The request could not be completed.';
    body.textContent = reason;
  } else if (data.module === 'A') {
    // Crop Recommendation
    title.textContent = 'Top crop candidates';
    const list = document.createElement('ol');
    list.style.cssText = 'padding-left:1.25rem;margin:0;display:flex;flex-direction:column;gap:0.5rem;';
    result.candidates.forEach((candidate) => {
      const item = document.createElement('li');
      item.style.color = 'var(--text-primary)';
      item.innerHTML = `<strong>${candidate.crop}</strong>
        <span style="color:var(--text-muted)"> · ${(candidate.model_score * 100).toFixed(1)}% model score</span>`;
      list.append(item);
    });
    body.append(list);
  } else if (data.module === 'B') {
    // Irrigation Advisory
    title.textContent = result.action === 'IRRIGATE' ? 'Irrigation indicated' : 'No irrigation needed';
    const desc = document.createElement('p');
    desc.style.margin = '0';
    desc.textContent = result.action === 'IRRIGATE'
      ? `Apply ${result.gross_depth_mm} mm gross depth, approximately ${result.volume_m3} m³ over ${result.target_area_ha} ha.`
      : `Projected depletion is ${result.projected_depletion_mm} mm, below the ${result.readily_available_water_mm} mm threshold. No irrigation needed.`;
    body.append(desc);
  } else if (data.module === 'C') {
    // Weather Advisory
    const count = result.alerts ? result.alerts.length : 0;
    title.textContent = count
      ? `${count} condition${count === 1 ? '' : 's'} flagged`
      : 'No alerts triggered';
    if (count > 0) {
      const list = document.createElement('ul');
      list.style.cssText = 'padding-left:1.25rem;margin:0;display:flex;flex-direction:column;gap:0.5rem;';
      result.alerts.forEach((alert) => {
        const item = document.createElement('li');
        item.style.color = 'var(--text-primary)';
        item.innerHTML = `<strong>${alert.flag.replaceAll('_', ' ')}</strong>
          <span style="color:var(--text-muted)"> — ${alert.action}</span>`;
        list.append(item);
      });
      body.append(list);
    } else {
      body.textContent = 'Weather conditions are within normal parameters for the next 24 hours.';
    }
  } else if (data.module === 'D') {
    // Sustainability Scoring
    title.textContent = `Sustainability Score: ${result.score.toFixed(2)} / 100`;
    const desc = document.createElement('p');
    desc.style.margin = '0 0 0.75rem';
    desc.textContent = result.yield_gate_applied
      ? 'The resource score was capped because yield retention fell below 95%. Ensure crop health is maintained.'
      : `Yield retention: ${(result.yield_retention_ratio * 100).toFixed(1)}%. Formula version ${result.formula_version}.`;
    body.append(desc);

    // Component score breakdown
    if (result.component_scores) {
      const breakdown = document.createElement('div');
      breakdown.style.cssText = 'display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-top:0.25rem;';
      Object.entries(result.component_scores).forEach(([key, value]) => {
        const card = document.createElement('div');
        card.style.cssText = 'padding:0.75rem;background:var(--surface-alt);border:1px solid var(--border);border-radius:0.5rem;';
        card.innerHTML = `
          <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.25rem;text-transform:capitalize;">${key}</div>
          <div style="font-size:1.1rem;font-weight:700;color:var(--text-primary);">${value.toFixed(1)}</div>
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
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!output) return;
    
    // Clear previous results
    output.innerHTML = '';
    
    // Show leaf loader
    LeafLoader.show(output, 'Analyzing soil and climate data...');
    
    // Set button loading state
    if (submitBtn) {
      LeafLoader.setButtonLoading(submitBtn, true);
    }
    
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
      LeafLoader.hide(output);
      displayResult(data, output);
    } catch (error) {
      LeafLoader.hide(output);
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module A error:', error);
    } finally {
      if (submitBtn) {
        LeafLoader.setButtonLoading(submitBtn, false);
      }
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
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!output) return;
    
    // Clear previous results
    output.innerHTML = '';
    
    // Show leaf loader
    LeafLoader.show(output, 'Calculating water balance...');
    
    // Set button loading state
    if (submitBtn) {
      LeafLoader.setButtonLoading(submitBtn, true);
    }
    
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
      LeafLoader.hide(output);
      displayResult(data, output);
    } catch (error) {
      LeafLoader.hide(output);
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module B error:', error);
    } finally {
      if (submitBtn) {
        LeafLoader.setButtonLoading(submitBtn, false);
      }
    }
  });
}

/**
 * Initialize Module C - Weather Advisory
 */
function initModuleC() {
  const form = DOM.byId('weather-form');
  const demoBtn = DOM.byId('weather-demo');
  const locationBtn = DOM.byId('useWeatherLocation');
  
  if (!form) return;

  if (locationBtn) {
    locationBtn.addEventListener('click', () => {
      const status = DOM.byId('weatherLocationStatus');
      const latInput = form.querySelector('input[name="latitude"]');
      const lonInput = form.querySelector('input[name="longitude"]');

      if (!navigator.geolocation) {
        if (status) status.textContent = 'Location is unavailable in your browser. Enter coordinates manually.';
        return;
      }

      if (status) status.textContent = 'Getting your location…';
      navigator.geolocation.getCurrentPosition(
        ({ coords }) => {
          if (latInput) latInput.value = coords.latitude.toFixed(4);
          if (lonInput) lonInput.value = coords.longitude.toFixed(4);
          if (status) status.textContent = 'Location ready. Coordinates updated.';
        },
        (err) => {
          if (status) status.textContent = 'Unable to retrieve location. Please check browser permissions or enter manually.';
          console.warn('Geolocation error:', err);
        },
        { timeout: 10000 }
      );
    });
  }
  
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
  const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
  const demoBtn = DOM.byId('weather-demo');

  if (!form || !output) return;

  // Clear previous results and show leaf loader
  output.innerHTML = '';
  LeafLoader.show(output, 'Fetching weather forecast...');

  // Set button loading states
  if (submitBtn && !isDemo) LeafLoader.setButtonLoading(submitBtn, true);
  if (demoBtn && isDemo) LeafLoader.setButtonLoading(demoBtn, true);

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
    LeafLoader.hide(output);
    displayResult(data, output);
  } catch (error) {
    LeafLoader.hide(output);
    UI.showError(output, 'Request failed. Please try again.');
    console.error('Module C error:', error);
  } finally {
    if (submitBtn && !isDemo) LeafLoader.setButtonLoading(submitBtn, false);
    if (demoBtn && isDemo) LeafLoader.setButtonLoading(demoBtn, false);
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
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!output) return;

    // Clear previous results and show leaf loader
    output.innerHTML = '';
    LeafLoader.show(output, 'Computing sustainability score...');
    if (submitBtn) LeafLoader.setButtonLoading(submitBtn, true);

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
      LeafLoader.hide(output);
      displayResult(data, output);
    } catch (error) {
      LeafLoader.hide(output);
      UI.showError(output, 'Request failed. Please try again.');
      console.error('Module D error:', error);
    } finally {
      if (submitBtn) LeafLoader.setButtonLoading(submitBtn, false);
    }
  });
}

/**
 * Initialize Module E: Grounded GenAI Conversational Agronomist
 */
function initModuleE() {
  const langSelect = DOM.byId('advisory-assistant-lang');
  const chatLog = DOM.byId('advisory-chat-log');
  const chatForm = DOM.byId('advisory-chat-form');
  const chatInput = DOM.byId('advisory-chat-input');
  const sendBtn = DOM.byId('advisory-chat-send');
  const chipContainer = DOM.byId('advisory-prompt-chips');

  if (!chatForm || !chatInput || !chatLog) return;

  let currentLang = langSelect ? langSelect.value : 'en';
  const sessionId = 'advisory-session-' + Math.random().toString(36).slice(2);

  function getActiveDashboardContext() {
    const cropForm = DOM.byId('crop-form');
    const irrigationForm = DOM.byId('irrigation-form');
    const weatherForm = DOM.byId('weather-form');

    return {
      core_detection: {
        crop: 'General Crop Farm Advisory',
        severity: 'none',
        description: 'Active precision agriculture dashboard session.',
        precautions: [
          'Maintain balanced soil NPK ratios according to local soil test reports.',
          'Align irrigation scheduling with projected 24-hour evapotranspiration.',
          'Monitor real-time weather alerts for frost, extreme heat, or high winds.'
        ]
      },
      soil: cropForm ? {
        nitrogen: getNumber(cropForm, 'N'),
        phosphorus: getNumber(cropForm, 'P'),
        potassium: getNumber(cropForm, 'K'),
        ph: getNumber(cropForm, 'ph'),
      } : null,
      irrigation_recommendation_bonus_B: irrigationForm ? {
        soil_moisture: getNumber(irrigationForm, 'moisture'),
        field_capacity: getNumber(irrigationForm, 'fieldCapacity'),
        forecast_et0: getNumber(irrigationForm, 'et0'),
      } : null,
      weather_bonus_C: weatherForm ? {
        latitude: getNumber(weatherForm, 'latitude'),
        longitude: getNumber(weatherForm, 'longitude'),
      } : null,
    };
  }

  function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    if (role === 'user') {
      // User bubble: dark green bg, white text — works in both modes
      msgDiv.className = 'p-3 rounded-lg text-sm ml-6';
      msgDiv.style.cssText = 'background-color:#176a46; color:#ffffff;';
      msgDiv.innerHTML = `<span class="text-xs font-semibold block mb-1" style="color:#a8e6c4;">You:</span> ${DOM.escapeHtml(text)}`;
    } else {
      // Assistant bubble: uses CSS vars so it adapts to light/dark mode
      msgDiv.className = 'p-3 rounded-lg text-sm mr-6';
      msgDiv.style.cssText = 'background-color:var(--surface); border:1px solid var(--border); color:var(--text-primary);';
      msgDiv.innerHTML = `<span class="text-xs font-bold block mb-1" style="color:var(--primary);">AgriSmart AI Assistant:</span> ${DOM.escapeHtml(text).replace(/\n/g, '<br>')}`;
    }
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  async function sendChatMessage(message) {
    if (!message || !chatLog) return;
    appendMessage('user', message);

    // Show inline LeafLoader in chat
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'p-3 rounded-lg text-sm mr-6';
    loadingDiv.style.cssText = 'background-color:var(--surface); border:1px solid var(--border); color:var(--text-primary);';
    loadingDiv.dataset.loadingMsg = 'true';

    const loader = LeafLoader.createInline('Consulting agronomic knowledge base…');
    loadingDiv.innerHTML = `<span class="text-xs font-bold block mb-1" style="color:var(--primary);">AgriSmart AI Assistant:</span>`;
    loadingDiv.appendChild(loader);
    chatLog.appendChild(loadingDiv);
    chatLog.scrollTop = chatLog.scrollHeight;

    if (sendBtn) {
      LeafLoader.setButtonLoading(sendBtn, true);
    }

    try {
      const response = await API.chatAssistant({
        session_id: sessionId,
        message:    message,
        context:    getActiveDashboardContext(),
        lang:       currentLang,
      });

      loadingDiv.remove();

      if (response && response.reply) {
        appendMessage('assistant', response.reply);
      } else {
        appendMessage('assistant', 'I could not process that question. Please try asking about crops, soil, irrigation, or weather.');
      }
    } catch (err) {
      loadingDiv.remove();
      appendMessage('assistant', 'Unable to reach the advisory service. Please check your connection and try again.');
      console.error('Advisory assistant error:', err);
    } finally {
      loadingDiv.remove();
      if (sendBtn) {
        LeafLoader.setButtonLoading(sendBtn, false);
      }
    }
  }

  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      currentLang = e.target.value;
    });
  }

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = '';
    sendChatMessage(msg);
  });

  if (chipContainer) {
    chipContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('button[data-prompt]');
      if (chip && chip.dataset.prompt) {
        sendChatMessage(chip.dataset.prompt);
      }
    });
  }
}

export { initModuleA, initModuleB, initModuleC, initModuleD, initModuleE };

