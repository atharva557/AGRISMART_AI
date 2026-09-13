/**
 * AgriSmart AI - Utility Functions
 * Helper functions used across the application
 */

const Utils = {
  /**
   * Format a date to a readable string
   * @param {Date|string} date - Date object or ISO string
   * @param {string} format - 'short' | 'long' | 'time'
   * @returns {string}
   */
  formatDate(date, format = 'short') {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(d.getTime())) {
      return 'Invalid date';
    }
    
    const options = {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
      time: { hour: '2-digit', minute: '2-digit', second: '2-digit' }
    };
    
    return d.toLocaleDateString('en-US', options[format] || options.short);
  },

  /**
   * Format a number with specified decimal places
   * @param {number} number - Number to format
   * @param {number} decimals - Number of decimal places
   * @returns {string}
   */
  formatNumber(number, decimals = 2) {
    if (typeof number !== 'number' || isNaN(number)) {
      return '0';
    }
    return number.toFixed(decimals);
  },

  /**
   * Debounce a function
   * @param {Function} func - Function to debounce
   * @param {number} delay - Delay in milliseconds
   * @returns {Function}
   */
  debounce(func, delay = 300) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  },

  /**
   * Throttle a function
   * @param {Function} func - Function to throttle
   * @param {number} limit - Time limit in milliseconds
   * @returns {Function}
   */
  throttle(func, limit = 300) {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },

  /**
   * Get element by ID
   * @param {string} id - Element ID
   * @returns {HTMLElement|null}
   */
  byId(id) {
    return document.getElementById(id);
  },

  /**
   * Query selector helper
   * @param {string} selector - CSS selector
   * @param {HTMLElement} parent - Parent element (default: document)
   * @returns {HTMLElement|null}
   */
  qs(selector, parent = document) {
    return parent.querySelector(selector);
  },

  /**
   * Query selector all helper
   * @param {string} selector - CSS selector
   * @param {HTMLElement} parent - Parent element (default: document)
   * @returns {NodeList}
   */
  qsa(selector, parent = document) {
    return parent.querySelectorAll(selector);
  },

  /**
   * Add event listener to multiple elements
   * @param {NodeList|Array} elements - Elements to attach listener to
   * @param {string} event - Event name
   * @param {Function} handler - Event handler
   */
  addEventListeners(elements, event, handler) {
    elements.forEach(el => el.addEventListener(event, handler));
  },

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string}
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  /**
   * Generate unique ID
   * @param {string} prefix - Optional prefix
   * @returns {string}
   */
  uniqueId(prefix = 'id') {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Copy text to clipboard
   * @param {string} text - Text to copy
   * @returns {Promise<boolean>}
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      return false;
    }
  },

  /**
   * Format file size
   * @param {number} bytes - Size in bytes
   * @returns {string}
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },

  /**
   * Parse query string
   * @param {string} queryString - Query string (default: window.location.search)
   * @returns {Object}
   */
  parseQueryString(queryString = window.location.search) {
    const params = new URLSearchParams(queryString);
    const result = {};
    for (const [key, value] of params) {
      result[key] = value;
    }
    return result;
  },

  /**
   * Scroll to element smoothly
   * @param {HTMLElement|string} element - Element or selector
   * @param {number} offset - Offset from top (default: 0)
   */
  scrollTo(element, offset = 0) {
    const el = typeof element === 'string' ? this.qs(element) : element;
    if (!el) return;
    
    const top = el.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  },

  /**
   * Check if element is in viewport
   * @param {HTMLElement} element - Element to check
   * @returns {boolean}
   */
  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  },

  /**
   * Local storage helpers
   */
  storage: {
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (error) {
        console.error('LocalStorage set error:', error);
        return false;
      }
    },

    get(key, defaultValue = null) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (error) {
        console.error('LocalStorage get error:', error);
        return defaultValue;
      }
    },

    remove(key) {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (error) {
        console.error('LocalStorage remove error:', error);
        return false;
      }
    },

    clear() {
      try {
        localStorage.clear();
        return true;
      } catch (error) {
        console.error('LocalStorage clear error:', error);
        return false;
      }
    }
  },

  /**
   * Check if device is mobile
   * @returns {boolean}
   */
  isMobile() {
    return window.innerWidth < 768;
  },

  /**
   * Wait for specified time
   * @param {number} ms - Milliseconds to wait
   * @returns {Promise}
   */
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  /**
   * Capitalize first letter
   * @param {string} str - String to capitalize
   * @returns {string}
   */
  capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  /**
   * Truncate text
   * @param {string} text - Text to truncate
   * @param {number} length - Maximum length
   * @param {string} suffix - Suffix to add (default: '...')
   * @returns {string}
   */
  truncate(text, length, suffix = '...') {
    if (!text || text.length <= length) return text;
    return text.substring(0, length) + suffix;
  }
};

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Utils;
}
