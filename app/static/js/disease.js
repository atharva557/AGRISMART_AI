/**
 * AgriSmart AI - Disease Detection
 * Handle image upload and disease prediction
 */

const DiseaseDetection = {
  currentFile: null,
  uploadProgress: 0,

  /**
   * Initialize disease detection page
   */
  init() {
    const uploadInput = Utils.byId('imageUpload');
    const uploadArea = Utils.byId('uploadArea');
    const previewContainer = Utils.byId('imagePreview');
    const uploadBtn = Utils.byId('uploadBtn');
    const clearBtn = Utils.byId('clearBtn');
    const analyzeBtn = Utils.byId('analyzeBtn');

    // Setup file input
    if (uploadInput) {
      FileUpload.setupFileInput(uploadInput, (file) => this.handleFileSelect(file));
    }

    // Setup drag and drop
    if (uploadArea) {
      FileUpload.setupDragAndDrop(uploadArea, (file) => this.handleFileSelect(file));
    }

    // Clear button
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearSelection());
    }

    // Analyze button
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => this.analyzeImage());
    }
  },

  /**
   * Handle file selection
   * @param {File} file - Selected file
   */
  async handleFileSelect(file) {
    const previewContainer = Utils.byId('imagePreview');
    const errorContainer = Utils.byId('uploadError');
    const analyzeBtn = Utils.byId('analyzeBtn');
    const clearBtn = Utils.byId('clearBtn');

    // Clear previous errors
    if (errorContainer) {
      errorContainer.innerHTML = '';
    }

    // Validate file
    const validation = FileUpload.validateFile(file);
    if (!validation.valid) {
      UI.showError(errorContainer, validation.error, 'Invalid File');
      return;
    }

    // Store file
    this.currentFile = file;

    // Create preview
    try {
      await FileUpload.createPreview(file, previewContainer);
      
      // Show action buttons
      if (analyzeBtn) UI.show(analyzeBtn);
      if (clearBtn) UI.show(clearBtn);
      
      // Hide upload area label
      const uploadLabel = Utils.qs('#uploadArea label');
      if (uploadLabel) uploadLabel.style.display = 'none';
    } catch (error) {
      UI.showError(errorContainer, 'Failed to preview image. Please try another file.', 'Preview Error');
    }
  },

  /**
   * Clear file selection
   */
  clearSelection() {
    const uploadInput = Utils.byId('imageUpload');
    const previewContainer = Utils.byId('imagePreview');
    const errorContainer = Utils.byId('uploadError');
    const analyzeBtn = Utils.byId('analyzeBtn');
    const clearBtn = Utils.byId('clearBtn');
    const uploadLabel = Utils.qs('#uploadArea label');

    // Clear file
    this.currentFile = null;
    if (uploadInput) uploadInput.value = '';

    // Clear preview
    FileUpload.clearPreview(previewContainer);

    // Clear errors
    if (errorContainer) errorContainer.innerHTML = '';

    // Hide action buttons
    if (analyzeBtn) UI.hide(analyzeBtn);
    if (clearBtn) UI.hide(clearBtn);

    // Show upload label
    if (uploadLabel) uploadLabel.style.display = 'flex';
  },

  /**
   * Analyze image
   */
  async analyzeImage() {
    if (!this.currentFile) {
      UI.toast('Please select an image first', 'error');
      return;
    }

    const resultContainer = Utils.byId('analysisResult');
    const analyzeBtn = Utils.byId('analyzeBtn');

    // Disable button
    if (analyzeBtn) {
      UI.disable(analyzeBtn);
      analyzeBtn.innerHTML = `
        <div class="spinner spinner-sm"></div>
        <span>Analyzing...</span>
      `;
    }

    // Show loading in result container
    if (resultContainer) {
      UI.showLoading(resultContainer, 'Analyzing image with AI model...');
    }

    try {
      // Upload and analyze
      const response = await API.predictDisease(this.currentFile, (progress) => {
        this.uploadProgress = progress;
        // Update progress if needed
      });

      // Hide loading
      if (resultContainer) {
        UI.hideLoading(resultContainer);
      }

      // Handle response
      if (API.isSuccess(response)) {
        // Store result and redirect
        Utils.storage.set('disease_result', {
          result: response.result,
          image: await this.getImageDataUrl(this.currentFile),
          timestamp: new Date().toISOString()
        });
        window.location.href = '/disease/result';
      } else {
        // Show error
        const errorMessage = API.getErrorMessage(response);
        UI.showError(resultContainer, errorMessage, 'Analysis Failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      if (resultContainer) {
        UI.hideLoading(resultContainer);
        UI.showError(resultContainer, error.message || 'Failed to analyze image. Please try again.', 'Error');
      }
    } finally {
      // Re-enable button
      if (analyzeBtn) {
        UI.enable(analyzeBtn);
        analyzeBtn.innerHTML = `
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>Analyze Image</span>
        `;
      }
    }
  },

  /**
   * Get image data URL
   * @param {File} file - Image file
   * @returns {Promise<string>}
   */
  async getImageDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },

  /**
   * Display results on result page
   */
  displayResults() {
    const resultData = Utils.storage.get('disease_result');
    
    if (!resultData) {
      // No result data, redirect to upload
      window.location.href = '/disease';
      return;
    }

    const { result, image, timestamp } = resultData;
    const container = Utils.byId('resultContainer');

    if (!container) return;

    // Build result HTML
    const confidence = result.confidence || 0;
    const confidencePercent = (confidence * 100).toFixed(1);
    const confidenceClass = this.getConfidenceClass(confidence);
    const confidenceLabel = this.getConfidenceLabel(confidence);

    container.innerHTML = `
      <div class="max-w-4xl mx-auto">
        <!-- Image Preview -->
        <div class="card mb-6">
          <img src="${image}" alt="Analyzed crop" class="max-w-full max-h-96 mx-auto rounded-lg">
        </div>

        <!-- Results Card -->
        <div class="card">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-3xl font-bold text-gray-900 mb-2">${Utils.escapeHtml(result.disease_name || 'Unknown')}</h2>
              <p class="text-sm text-gray-500">Analyzed ${Utils.formatDate(timestamp, 'long')}</p>
            </div>
            <div class="confidence-badge ${confidenceClass}">
              ${confidencePercent}% ${confidenceLabel}
            </div>
          </div>

          ${confidence < 0.75 ? `
            <div class="alert alert-warning mb-4">
              <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              <div class="alert-content">
                <div class="alert-title">Low Confidence Prediction</div>
                <p class="alert-message">This prediction has low confidence. Please consult a local agricultural expert for confirmation.</p>
              </div>
            </div>
          ` : ''}

          ${result.description ? `
            <div class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Description</h3>
              <p class="text-gray-700 leading-relaxed">${Utils.escapeHtml(result.description)}</p>
            </div>
          ` : ''}

          ${result.recommendations && result.recommendations.length > 0 ? `
            <div class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Treatment Recommendations</h3>
              <ul class="space-y-2">
                ${result.recommendations.map(rec => `
                  <li class="flex items-start gap-2">
                    <svg class="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class="text-gray-700">${Utils.escapeHtml(rec)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>
          ` : ''}

          <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-300">
            <a href="/disease" class="btn btn-primary flex-1">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              Analyze Another Image
            </a>
            <a href="/" class="btn btn-secondary flex-1">
              Back to Home
            </a>
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Get confidence class for styling
   * @param {number} confidence - Confidence value (0-1)
   * @returns {string}
   */
  getConfidenceClass(confidence) {
    if (confidence >= 0.75) return 'confidence-high';
    if (confidence >= 0.50) return 'confidence-medium';
    return 'confidence-low';
  },

  /**
   * Get confidence label
   * @param {number} confidence - Confidence value (0-1)
   * @returns {string}
   */
  getConfidenceLabel(confidence) {
    if (confidence >= 0.75) return 'Confidence';
    if (confidence >= 0.50) return 'Medium Confidence';
    return 'Low Confidence';
  }
};

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DiseaseDetection;
}
