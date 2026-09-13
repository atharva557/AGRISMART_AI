/**
 * Formatting Utilities
 * Functions for formatting data for display
 */

export const Format = {
  /**
   * Format a date to a readable string
   * @param {Date|string} date - Date object or ISO string
   * @param {string} format - 'short' | 'long' | 'time'
   * @returns {string}
   */
  date(date, format = 'short') {
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
  number(number, decimals = 2) {
    if (typeof number !== 'number' || isNaN(number)) {
      return '0';
    }
    return number.toFixed(decimals);
  },

  /**
   * Format file size
   * @param {number} bytes - Size in bytes
   * @returns {string}
   */
  fileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
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
  },
};

export default Format;
