/**
 * AgriSmart AI - API Service
 * Centralized API communication layer
 */

const API = {
  baseURL: window.location.origin,
  
  /**
   * Make a GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Additional fetch options
   * @returns {Promise<Object>}
   */
  async get(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  },

  /**
   * Make a POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Additional fetch options
   * @returns {Promise<Object>}
   */
  async post(endpoint, data, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        body: JSON.stringify(data),
        ...options
      });
      
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  },

  /**
   * Upload file with multipart/form-data
   * @param {string} endpoint - API endpoint
   * @param {FormData} formData - Form data with file
   * @param {Function} onProgress - Progress callback (optional)
   * @returns {Promise<Object>}
   */
  async uploadFile(endpoint, formData, onProgress = null) {
    try {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // Progress tracking
        if (onProgress && xhr.upload) {
          xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
              const percentComplete = (e.loaded / e.total) * 100;
              onProgress(percentComplete);
            }
          });
        }
        
        // Load event
        xhr.addEventListener('load', () => {
          try {
            const response = JSON.parse(xhr.responseText);
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(response);
            } else {
              resolve(this.handleError({
                status: xhr.status,
                message: response.message || 'Upload failed',
                data: response
              }));
            }
          } catch (error) {
            reject(error);
          }
        });
        
        // Error event
        xhr.addEventListener('error', () => {
          reject(new Error('Network error during upload'));
        });
        
        // Abort event
        xhr.addEventListener('abort', () => {
          reject(new Error('Upload aborted'));
        });
        
        xhr.open('POST', `${this.baseURL}${endpoint}`);
        xhr.send(formData);
      });
    } catch (error) {
      return this.handleError(error);
    }
  },

  /**
   * Handle API response
   * @param {Response} response - Fetch response
   * @returns {Promise<Object>}
   */
  async handleResponse(response) {
    let data;
    
    try {
      data = await response.json();
    } catch (error) {
      // If response is not JSON
      data = {
        status: response.ok ? 'OK' : 'ERROR',
        message: response.statusText || 'Request failed',
        result: null
      };
    }
    
    // Add HTTP status to response
    data.httpStatus = response.status;
    
    return data;
  },

  /**
   * Handle API errors
   * @param {Error|Object} error - Error object
   * @returns {Object}
   */
  handleError(error) {
    console.error('API Error:', error);
    
    return {
      status: 'ERROR',
      message: error.message || 'An unexpected error occurred',
      result: null,
      httpStatus: error.status || 0,
      error: true
    };
  },

  /**
   * Health check endpoint
   * @returns {Promise<boolean>}
   */
  async checkHealth() {
    try {
      const data = await this.get('/api/health');
      return data.status === 'ok';
    } catch (error) {
      return false;
    }
  },

  /**
   * Disease Detection - Predict disease from image
   * @param {File} imageFile - Image file to analyze
   * @param {Function} onProgress - Progress callback
   * @returns {Promise<Object>}
   */
  async predictDisease(imageFile, onProgress = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    return await this.uploadFile('/api/disease/predict', formData, onProgress);
  },

  /**
   * Module A - Crop Recommendation
   * @param {Object} data - Request payload
   * @returns {Promise<Object>}
   */
  async recommendCrops(data) {
    return await this.post('/api/crops/recommend', data);
  },

  /**
   * Module B - Irrigation Advisory
   * @param {Object} data - Request payload
   * @returns {Promise<Object>}
   */
  async adviseIrrigation(data) {
    return await this.post('/api/irrigation/advise', data);
  },

  /**
   * Module C - Weather Advisory
   * @param {Object} data - Request payload
   * @returns {Promise<Object>}
   */
  async adviseWeather(data) {
    return await this.post('/api/weather/advise', data);
  },

  /**
   * Module D - Sustainability Scoring
   * @param {Object} data - Request payload
   * @returns {Promise<Object>}
   */
  async scoreSustainability(data) {
    return await this.post('/api/sustainability/score', data);
  },

  /**
   * Module E - Assistant Chat (not implemented)
   * @param {Object} data - Request payload
   * @returns {Promise<Object>}
   */
  async assistantChat(data) {
    return await this.post('/api/assistant/chat', data);
  },

  /**
   * Create request envelope for advisory modules
   * @param {string} module - Module letter (A, B, C, D)
   * @param {string} purpose - Purpose (farm_advisory, simulation, dataset_benchmark)
   * @param {Object} inputs - Module-specific inputs
   * @param {Object} farm - Farm metadata (optional)
   * @param {Object} cropContext - Crop context (optional)
   * @returns {Object}
   */
  createEnvelope(module, purpose, inputs, farm = null, cropContext = null) {
    return {
      contract_version: '0.1.0',
      request_id: `${module}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      module: module,
      purpose: purpose,
      as_of_utc: new Date().toISOString(),
      farm: farm,
      crop_context: cropContext,
      inputs: inputs
    };
  },

  /**
   * Create evidence object for measurements
   * @param {string} kind - Evidence kind (observed, forecast, assumed, etc.)
   * @param {string} source - Evidence source
   * @param {string} method - Measurement method
   * @returns {Object}
   */
  createEvidence(kind = 'assumed', source = 'AgriSmart UI', method = 'User input') {
    return {
      kind: kind,
      source: source,
      method: method,
      observed_at_utc: new Date().toISOString(),
      period_start_utc: null,
      period_end_utc: null,
      reference_id: kind === 'assumed' ? 'ui-input' : null
    };
  },

  /**
   * Create measurement object
   * @param {number} value - Measurement value
   * @param {string} unit - Unit of measurement
   * @param {string} kind - Evidence kind
   * @returns {Object}
   */
  createMeasurement(value, unit, kind = 'assumed') {
    return {
      value: value,
      unit: unit,
      evidence: this.createEvidence(kind)
    };
  },

  /**
   * Check if response indicates success
   * @param {Object} response - API response
   * @returns {boolean}
   */
  isSuccess(response) {
    return ['OK', 'EXPERIMENTAL', 'SIMULATED'].includes(response.status);
  },

  /**
   * Check if response indicates error
   * @param {Object} response - API response
   * @returns {boolean}
   */
  isError(response) {
    return ['NEEDS_DATA', 'INVALID_INPUT', 'UNSUPPORTED_CONTEXT', 
            'STALE_DATA', 'DATA_UNAVAILABLE', 'ERROR'].includes(response.status);
  },

  /**
   * Get user-friendly error message
   * @param {Object} response - API response
   * @returns {string}
   */
  getErrorMessage(response) {
    if (response.message) {
      return response.message;
    }
    
    if (response.reasons && response.reasons.length > 0) {
      return response.reasons[0].message;
    }
    
    const statusMessages = {
      'NEEDS_DATA': 'Required data is missing. Please check your inputs.',
      'INVALID_INPUT': 'Invalid input provided. Please check your data.',
      'UNSUPPORTED_CONTEXT': 'This operation is not supported in the current context.',
      'STALE_DATA': 'Data is too old. Please refresh and try again.',
      'DATA_UNAVAILABLE': 'Required data or service is currently unavailable.',
      'ERROR': 'An error occurred. Please try again.'
    };
    
    return statusMessages[response.status] || 'An unexpected error occurred.';
  }
};

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API;
}
