/**
 * Disease Detection Page
 */

import API from '../core/api.js';
import UI from '../components/ui.js';
import DOM from '../utils/dom.js';
import { Format } from '../utils/format.js';
import { buildDiseaseAssistantPayload } from '../utils/assistant-context.mjs';

// State
let selectedFile = null;

// Initialize disease detection page
document.addEventListener('DOMContentLoaded', () => {
  console.log('Disease detection page loaded');
  
  initFileUpload();
  initAnalyzeButton();
});

/**
 * Initialize file upload functionality
 */
function initFileUpload() {
  const uploadInput = DOM.byId('imageUpload');
  const uploadArea = DOM.byId('uploadArea');
  const previewContainer = DOM.byId('imagePreview');
  
  if (!uploadInput || !uploadArea) return;
  
  // File input change
  uploadInput.addEventListener('change', handleFileSelect);
  
  // Drag and drop
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('border-green-500', 'bg-green-50');
  });
  
  uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-green-500', 'bg-green-50');
  });
  
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-green-500', 'bg-green-50');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadInput.files = files;
      handleFileSelect({ target: uploadInput });
    }
  });
}

/**
 * Handle file selection
 * @param {Event} event
 */
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Validate file
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  if (!validTypes.includes(file.type)) {
    UI.toast('Please select a JPG or PNG image', 'error');
    return;
  }
  
  if (file.size > maxSize) {
    UI.toast('File size must be less than 10MB', 'error');
    return;
  }
  
  // Clear any previous results and errors
  const resultContainer = DOM.byId('analysisResult') || DOM.byId('result');
  const errorContainer = DOM.byId('uploadError');
  if (resultContainer) resultContainer.innerHTML = '';
  if (errorContainer) errorContainer.innerHTML = '';

  selectedFile = file;
  displayPreview(file);
  showAnalyzeButton();
}

/**
 * Display image preview
 * @param {File} file
 */
function displayPreview(file) {
  const previewContainer = DOM.byId('imagePreview');
  const uploadLabel = DOM.byId('uploadLabel');
  
  // Hide the initial upload prompt & Choose Image button
  if (uploadLabel) {
    uploadLabel.classList.add('hidden');
    uploadLabel.style.display = 'none';
  }
  
  if (!previewContainer) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    previewContainer.innerHTML = `
      <div class="space-y-3">
        <img src="${e.target.result}" 
             alt="Selected crop image" 
             class="max-h-72 w-auto mx-auto rounded-xl border border-gray-200 shadow-sm object-contain">
        <div class="flex items-center justify-between text-xs text-gray-500 max-w-sm mx-auto px-2">
          <span class="font-medium text-gray-700 truncate max-w-[220px]">${DOM.escapeHtml(file.name)}</span>
          <span class="font-semibold">${Format.fileSize(file.size)}</span>
        </div>
      </div>
    `;
  };
  reader.readAsDataURL(file);
}

/**
 * Show analyze button
 */
function showAnalyzeButton() {
  const analyzeBtn = DOM.byId('analyzeBtn');
  const clearBtn = DOM.byId('clearBtn');
  
  if (analyzeBtn) {
    analyzeBtn.classList.remove('hidden');
  }
  
  if (clearBtn) {
    clearBtn.classList.remove('hidden');
  }
}

/**
 * Initialize analyze button
 */
function initAnalyzeButton() {
  const analyzeBtn = DOM.byId('analyzeBtn');
  const clearBtn = DOM.byId('clearBtn');
  
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', handleAnalyze);
  }
  
  if (clearBtn) {
    clearBtn.addEventListener('click', handleClear);
  }
}

/**
 * Handle analyze button click
 */
async function handleAnalyze() {
  if (!selectedFile) {
    UI.toast('Please select an image first', 'warning');
    return;
  }
  
  const resultContainer = DOM.byId('analysisResult');
  if (!resultContainer) return;
  
  UI.showLoading(resultContainer, 'Analyzing image...');
  
  try {
    const response = await API.predictDisease(selectedFile, (progress) => {
      console.log(`Upload progress: ${progress.toFixed(0)}%`);
    });
    
    if (API.isSuccess(response)) {
      displayResult(response, resultContainer);
    } else {
      const errorMessage = API.getErrorMessage(response);
      UI.showError(resultContainer, errorMessage, 'Analysis Failed');
    }
  } catch (error) {
    UI.showError(resultContainer, 'An unexpected error occurred. Please try again.', 'Error');
    console.error('Analysis error:', error);
  }
}

/**
 * Display analysis result
 * @param {Object} response
 * @param {HTMLElement} container
 */
function displayResult(response, container) {
  const result = response.result;
  
  if (!result) {
    UI.showError(container, 'No result received from the server', 'Error');
    return;
  }
  
  const confidence = result.confidence || 0;
  const confidencePercent = (confidence * 100).toFixed(1);
  const isHealthy = (result.disease || '').toLowerCase() === 'healthy';
  
  const isLowConfidence = confidence < 0.75;
  let confidenceBadgeClass = 'bg-emerald-100 text-emerald-800 border-emerald-300';
  let confidenceText = 'High Confidence';
  if (isLowConfidence) {
    confidenceBadgeClass = 'bg-amber-100 text-amber-800 border-amber-300';
    confidenceText = 'Low Confidence (< 75%)';
  } else if (confidence < 0.85) {
    confidenceBadgeClass = 'bg-blue-100 text-blue-800 border-blue-300';
    confidenceText = 'Moderate Confidence';
  }

  const severity = isLowConfidence ? 'Triage Required' : (result.severity || 'moderate').toLowerCase();
  let severityBadgeClass = 'bg-amber-100 text-amber-800';
  if (!isLowConfidence && severity === 'none') severityBadgeClass = 'bg-emerald-100 text-emerald-800';
  else if (!isLowConfidence && severity === 'high') severityBadgeClass = 'bg-rose-100 text-rose-800';
  else if (!isLowConfidence && severity === 'low') severityBadgeClass = 'bg-blue-100 text-blue-800';

  // Normalize recommendations & symptoms
  const recommendations = Array.isArray(result.recommendations) 
    ? result.recommendations 
    : (result.recommendations ? [result.recommendations] : []);
  const symptoms = Array.isArray(result.symptoms) ? result.symptoms : (result.symptoms ? [result.symptoms] : []);

  // Banner background and titles based on confidence state
  let bannerBg = isHealthy ? 'bg-[#0f4c3a]' : 'bg-[#15352b]';
  let bannerTag = isHealthy ? 'Healthy Foliage Assessment' : 'Pathology Diagnostic Report';
  let conditionTitle = `<span class="text-white">${DOM.escapeHtml(result.crop || 'Plant')}:</span> <span class="${isHealthy ? 'text-emerald-300' : 'text-[#dcefa8]'} font-semibold">${DOM.escapeHtml(result.disease || 'Detected Condition')}</span>`;
  
  if (isLowConfidence) {
    bannerBg = 'bg-[#4a3410]';
    bannerTag = 'Inconclusive / Low Confidence Assessment';
    conditionTitle = `<span class="text-white">${DOM.escapeHtml(result.crop || 'Plant')}:</span> <span class="text-amber-200 font-semibold">Unconfirmed (Possible: ${DOM.escapeHtml(result.disease || 'Condition')})</span>`;
  }

  container.innerHTML = `
    <div class="mt-8 bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden animate-fade-in transition-all">
      
      <!-- Top Header Banner -->
      <div class="p-6 sm:p-7 ${bannerBg} text-white flex flex-wrap items-center justify-between gap-4 border-b border-black/10">
        <div class="space-y-1.5">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold uppercase tracking-wider bg-white/10 ${isLowConfidence ? 'text-amber-300' : 'text-emerald-300'} border border-white/10">
            <svg class="w-3.5 h-3.5 ${isLowConfidence ? 'text-amber-400' : 'text-emerald-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            ${bannerTag}
          </div>
          <h3 class="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            ${conditionTitle}
          </h3>
        </div>
        
        <div class="px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-right">
          <p class="text-[11px] ${isLowConfidence ? 'text-amber-200' : 'text-gray-300'} uppercase tracking-wider font-medium">Confidence Score</p>
          <p class="text-2xl font-bold text-white tracking-tight">${confidencePercent}%</p>
        </div>
      </div>

      <div class="p-6 sm:p-7 space-y-6">
        
        <!-- Metrics Matrix -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="p-3.5 bg-gray-50 border border-gray-200/70 rounded-lg">
            <div class="flex items-center gap-1.5 text-gray-500 mb-1">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="text-[11px] font-semibold uppercase tracking-wider">Crop Species</span>
            </div>
            <p class="text-base font-bold text-gray-900">${DOM.escapeHtml(result.crop || 'N/A')}</p>
          </div>

          <div class="p-3.5 bg-gray-50 border border-gray-200/70 rounded-lg">
            <div class="flex items-center gap-1.5 text-gray-500 mb-1">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <span class="text-[11px] font-semibold uppercase tracking-wider">Identified Condition</span>
            </div>
            <p class="text-base font-bold ${isLowConfidence ? 'text-amber-800' : (isHealthy ? 'text-emerald-700' : 'text-rose-700')}">
              ${isLowConfidence ? `Unconfirmed (Possible: ${DOM.escapeHtml(result.disease || 'Unknown')})` : DOM.escapeHtml(result.disease || 'None')}
            </p>
          </div>

          <div class="p-3.5 bg-gray-50 border border-gray-200/70 rounded-lg">
            <div class="flex items-center gap-1.5 text-gray-500 mb-1">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              <span class="text-[11px] font-semibold uppercase tracking-wider">Severity Level</span>
            </div>
            <span class="inline-block px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide ${severityBadgeClass}">
              ${DOM.escapeHtml(severity)}
            </span>
          </div>

          <div class="p-3.5 bg-gray-50 border border-gray-200/70 rounded-lg">
            <div class="flex items-center gap-1.5 text-gray-500 mb-1">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="text-[11px] font-semibold uppercase tracking-wider">Reliability</span>
            </div>
            <span class="inline-block px-2 py-0.5 rounded text-xs font-semibold border ${confidenceBadgeClass}">
              ${confidenceText}
            </span>
          </div>
        </div>

        ${isLowConfidence ? `
          <div class="p-5 bg-amber-50 border-l-4 border-amber-500 rounded-r-lg space-y-2">
            <div class="flex items-center gap-2 text-amber-900 font-bold text-sm">
              <svg class="w-5 h-5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <span>Diagnosis Inconclusive — Model Confidence Below Safe Threshold (75%)</span>
            </div>
            <p class="text-sm text-amber-800 leading-relaxed">
              The AI model cannot confirm this pathology with high certainty (Confidence: <strong>${confidencePercent}%</strong>). The visual pattern suggests <strong>${DOM.escapeHtml(result.crop)}: ${DOM.escapeHtml(result.disease)}</strong> as a potential possibility, but it is not confirmed. Please consult a qualified agricultural extension officer or certified agronomist for field verification before applying any chemical treatment.
            </p>
          </div>
        ` : ''}

        <!-- Description Box -->
        ${result.description ? `
          <div class="p-4 bg-gray-50/80 border border-gray-200 rounded-lg">
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              ${isLowConfidence ? 'Potential Match Description (Reference Only)' : 'Pathological Description'}
            </h4>
            <p class="text-sm text-gray-700 leading-relaxed">${DOM.escapeHtml(result.description)}</p>
          </div>
        ` : ''}

        <!-- Symptoms Section -->
        ${symptoms.length > 0 ? `
          <div>
            <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2.5 flex items-center gap-2">
              <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              ${isLowConfidence ? 'Symptoms to Check for Field Verification' : 'Visible Symptoms'}
            </h4>
            <div class="grid sm:grid-cols-2 gap-2">
              ${symptoms.map(s => `
                <div class="flex items-start gap-2 p-2.5 bg-gray-50 border border-gray-200/60 rounded-md text-gray-700 text-sm">
                  <svg class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                  <span>${DOM.escapeHtml(s)}</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Recommendations & Treatments Section -->
        ${recommendations.length > 0 ? `
          <div>
            <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2.5 flex items-center gap-2">
              <svg class="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
              ${isLowConfidence ? 'General Preventative Actions (If Suspected)' : 'Recommended Agronomic Actions & Treatments'}
            </h4>
            <div class="space-y-2">
              ${recommendations.map(r => `
                <div class="flex items-start gap-3 p-3 bg-emerald-50/40 border border-emerald-200/60 rounded-lg text-gray-800 text-sm">
                  <svg class="w-4 h-4 text-emerald-700 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  <span class="leading-relaxed font-normal">${DOM.escapeHtml(r)}</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Module 6: Grounded GenAI Farmer Assistant Section -->
        <div class="mt-8 pt-6 border-t border-gray-200" id="assistantSection">
          <div class="bg-gradient-to-br from-emerald-900 to-emerald-950 rounded-xl p-6 text-white shadow-md">
            
            <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-white/10">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-emerald-700/60 border border-emerald-500/30 flex items-center justify-center text-emerald-200">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                  </svg>
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold uppercase tracking-wider text-emerald-300">Module 6</span>
                    <span class="text-xs px-2 py-0.5 rounded bg-emerald-800 text-emerald-200 font-medium">Grounded GenAI</span>
                  </div>
                  <h4 class="text-lg font-bold text-white">Farmer AI Advisory Assistant</h4>
                </div>
              </div>

              <!-- Language Selector -->
              <div class="flex items-center gap-2">
                <label for="assistantLang" class="text-xs text-emerald-200 font-medium">Language:</label>
                <select id="assistantLang" class="bg-emerald-800/90 text-white text-xs rounded-lg px-3 py-1.5 border border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-400 cursor-pointer">
                  <option value="en">English</option>
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="mr">मराठी (Marathi)</option>
                  <option value="gu">ગુજરાતી (Gujarati)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                  <option value="bn">বাংলা (Bengali)</option>
                  <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                </select>
              </div>
            </div>

            <!-- Explanation Box -->
            <div class="mt-4 p-4 bg-white/5 border border-white/10 rounded-lg">
              <div class="flex items-center gap-2 text-xs font-semibold text-emerald-300 uppercase tracking-wider mb-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Plain Language Guidance
              </div>
              <div id="assistantExplanationText" class="text-sm text-gray-200 leading-relaxed">
                Loading grounded explanation...
              </div>
            </div>

            <!-- Quick Action Prompt Chips -->
            <div class="mt-4">
              <p class="text-xs text-emerald-200 font-medium mb-2">Quick Follow-up Questions:</p>
              <div class="flex flex-wrap gap-2" id="assistantPromptChips">
                <button type="button" class="assistant-chip px-3 py-1 bg-white/10 hover:bg-white/20 border border-white/15 rounded-full text-xs text-white transition-all" data-prompt="What immediate precautions should I take?">What precautions should I take?</button>
                <button type="button" class="assistant-chip px-3 py-1 bg-white/10 hover:bg-white/20 border border-white/15 rounded-full text-xs text-white transition-all" data-prompt="Can this disease spread to other plants in my field?">Can this disease spread?</button>
                <button type="button" class="assistant-chip px-3 py-1 bg-white/10 hover:bg-white/20 border border-white/15 rounded-full text-xs text-white transition-all" data-prompt="How should I manage watering and irrigation for this condition?">How should I manage watering?</button>
              </div>
            </div>

            <!-- Chat History Log -->
            <div id="assistantChatLog" class="mt-4 space-y-3 max-h-60 overflow-y-auto pr-1 hidden"></div>

            <!-- Chat Input Form -->
            <form id="assistantChatForm" class="mt-4 flex gap-2">
              <input
                id="assistantChatInput"
                type="text"
                placeholder="Ask any follow-up question about this diagnosis..."
                class="flex-1 bg-white/10 border border-white/20 text-white placeholder-gray-400 text-sm rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
                autocomplete="off"
              />
              <button
                type="submit"
                id="assistantSendBtn"
                class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer">
                <span>Ask AI</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                </svg>
              </button>
            </form>

          </div>
        </div>

      </div>
    </div>
  `;

  // Initialize interactive assistant logic
  initAssistantSection(result);
}

/**
 * Initialize Module 6 Assistant Section
 * @param {Object} result - Disease prediction result object
 */
function initAssistantSection(result) {
  const langSelect = DOM.byId('assistantLang');
  const explanationEl = DOM.byId('assistantExplanationText');
  const chatLog = DOM.byId('assistantChatLog');
  const chatForm = DOM.byId('assistantChatForm');
  const chatInput = DOM.byId('assistantChatInput');
  const sendBtn = DOM.byId('assistantSendBtn');
  const chipContainer = DOM.byId('assistantPromptChips');

  let currentLang = langSelect ? langSelect.value : 'en';
  const sessionId = 'session-' + Math.random().toString(36).slice(2);
  let assistantContext = null;
  let explanationRequest = null;

  // The readable disease name cannot identify a crop-specific KB entry.
  let contextPayload;
  try {
    contextPayload = buildDiseaseAssistantPayload(result);
  } catch (error) {
    if (explanationEl) explanationEl.textContent = error.message;
    if (sendBtn) sendBtn.disabled = true;
    return;
  }

  async function loadExplanation() {
    if (!explanationEl) return;
    explanationEl.innerHTML = '<span class="text-emerald-300 animate-pulse">Consulting agronomic knowledge base...</span>';
    
    try {
      const response = await API.explainAssistant({ ...contextPayload, lang: currentLang });
      if (response && response.explanation && response.context) {
        explanationEl.innerHTML = DOM.escapeHtml(response.explanation).replace(/\n/g, '<br>');
        assistantContext = response.context;
        return assistantContext;
      } else {
        explanationEl.textContent = 'Grounded guidance could not be loaded. Please try again.';
      }
    } catch (err) {
      console.warn('Assistant explanation fetch failed:', err);
      explanationEl.textContent = 'Grounded guidance could not be loaded. Please check your connection.';
    }
    return null;
  }

  function appendChatMessage(role, text) {
    if (!chatLog) return;
    chatLog.classList.remove('hidden');
    
    const msgDiv = document.createElement('div');
    if (role === 'user') {
      msgDiv.className = 'p-3 bg-white/10 rounded-lg text-sm text-white ml-6 border border-white/10';
      msgDiv.innerHTML = `<span class="text-xs font-semibold text-emerald-300 block mb-1">Farmer:</span> ${DOM.escapeHtml(text)}`;
    } else {
      msgDiv.className = 'p-3 bg-emerald-800/80 rounded-lg text-sm text-emerald-50 mr-6 border border-emerald-600/40';
      msgDiv.innerHTML = `<span class="text-xs font-semibold text-emerald-300 block mb-1">AgriSmart AI Assistant:</span> ${DOM.escapeHtml(text).replace(/\n/g, '<br>')}`;
    }
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  async function sendChatMessage(message) {
    if (!message || !chatLog) return;
    appendChatMessage('user', message);
    
    // Loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'p-3 bg-emerald-800/40 rounded-lg text-sm text-emerald-200 mr-6 animate-pulse';
    loadingDiv.innerHTML = '<span class="text-xs font-semibold text-emerald-300 block mb-1">AgriSmart AI Assistant:</span> Processing answer...';
    chatLog.appendChild(loadingDiv);
    chatLog.scrollTop = chatLog.scrollHeight;

    if (sendBtn) sendBtn.disabled = true;

    try {
      // A fast click must not send a fabricated substitute for the server context.
      const context = assistantContext || await explanationRequest;
      if (!context) {
        appendChatMessage('assistant', 'The diagnosis context is not available yet. Please reload the explanation before asking a question.');
        return;
      }
      const response = await API.chatAssistant({
        session_id: sessionId,
        message: message,
        context,
        lang: currentLang,
      });

      loadingDiv.remove();

      if (response && response.reply) {
        appendChatMessage('assistant', response.reply);
      } else {
        appendChatMessage('assistant', 'I could not process that request. Please try asking about diagnosis, precautions, or irrigation.');
      }
    } catch (err) {
      loadingDiv.remove();
      appendChatMessage('assistant', 'Sorry, I could not complete the request. Please verify your connection.');
      console.error('Chat error:', err);
    } finally {
      loadingDiv.remove();
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  // Language Change Listener
  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      currentLang = e.target.value;
      explanationRequest = loadExplanation();
    });
  }

  // Chat Form Submit
  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const msg = chatInput.value.trim();
      if (!msg) return;
      chatInput.value = '';
      sendChatMessage(msg);
    });
  }

  // Quick Prompt Chips
  if (chipContainer) {
    chipContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.assistant-chip');
      if (chip && chip.dataset.prompt) {
        sendChatMessage(chip.dataset.prompt);
      }
    });
  }

  // Initial explanation load
  explanationRequest = loadExplanation();
}

/**
 * Handle clear button click
 */
function handleClear() {
  selectedFile = null;
  
  const uploadInput = DOM.byId('imageUpload');
  const previewContainer = DOM.byId('imagePreview');
  const analyzeBtn = DOM.byId('analyzeBtn');
  const clearBtn = DOM.byId('clearBtn');
  const resultContainer = DOM.byId('analysisResult') || DOM.byId('result');
  const errorContainer = DOM.byId('uploadError');
  const uploadLabel = DOM.byId('uploadLabel');
  
  if (uploadInput) uploadInput.value = '';
  if (previewContainer) previewContainer.innerHTML = '';
  if (analyzeBtn) analyzeBtn.classList.add('hidden');
  if (clearBtn) clearBtn.classList.add('hidden');
  if (resultContainer) resultContainer.innerHTML = '';
  if (errorContainer) errorContainer.innerHTML = '';
  if (uploadLabel) uploadLabel.style.display = 'flex';
}

export { handleAnalyze, handleClear };
