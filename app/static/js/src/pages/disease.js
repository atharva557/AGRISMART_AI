/**
 * Disease Detection Page
 */

import API from '../core/api.js';
import UI from '../components/ui.js';
import DOM from '../utils/dom.js';
import { Format } from '../utils/format.js';

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
  const uploadArea = DOM.qs('[role="button"][aria-label="Upload image area"]');
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
  if (!previewContainer) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    previewContainer.innerHTML = `
      <div class="mt-4 space-y-3">
        <img src="${e.target.result}" 
             alt="Selected crop image" 
             class="max-w-full h-auto rounded-lg border-2 border-gray-200 shadow-sm">
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>${DOM.escapeHtml(file.name)}</span>
          <span>${Format.fileSize(file.size)}</span>
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
  
  const resultContainer = DOM.byId('result');
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
  
  container.innerHTML = `
    <div class="space-y-4">
      <div class="alert alert-success">
        <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div class="alert-content">
          <div class="alert-title">Analysis Complete</div>
          <p class="alert-message">Disease detected: <strong>${DOM.escapeHtml(result.disease || 'Unknown')}</strong></p>
        </div>
      </div>
      
      ${result.confidence ? `
        <div class="p-4 bg-gray-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-1">Confidence</p>
          <p class="text-2xl font-bold text-gray-900">${(result.confidence * 100).toFixed(1)}%</p>
        </div>
      ` : ''}
      
      ${result.recommendations ? `
        <div class="p-4 border border-gray-200 rounded-lg">
          <h4 class="font-bold text-gray-900 mb-2">Recommendations</h4>
          <p class="text-gray-700">${DOM.escapeHtml(result.recommendations)}</p>
        </div>
      ` : ''}
    </div>
  `;
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
  const resultContainer = DOM.byId('result');
  
  if (uploadInput) uploadInput.value = '';
  if (previewContainer) previewContainer.innerHTML = '';
  if (analyzeBtn) analyzeBtn.classList.add('hidden');
  if (clearBtn) clearBtn.classList.add('hidden');
  if (resultContainer) resultContainer.innerHTML = '';
}

export { handleAnalyze, handleClear };
