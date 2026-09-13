/**
 * Validation Utilities
 * Input validation and sanitization
 */

export const Validation = {
  /**
   * Validate email address
   * @param {string} email
   * @returns {boolean}
   */
  isEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  },

  /**
   * Validate phone number (basic)
   * @param {string} phone
   * @returns {boolean}
   */
  isPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
  },

  /**
   * Validate URL
   * @param {string} url
   * @returns {boolean}
   */
  isURL(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Validate number range
   * @param {number} value
   * @param {number} min
   * @param {number} max
   * @returns {boolean}
   */
  isInRange(value, min, max) {
    const num = Number(value);
    return !isNaN(num) && num >= min && num <= max;
  },

  /**
   * Validate string length
   * @param {string} str
   * @param {number} min
   * @param {number} max
   * @returns {boolean}
   */
  isLengthValid(str, min, max) {
    const length = String(str).length;
    return length >= min && length <= max;
  },

  /**
   * Validate required field
   * @param {any} value
   * @returns {boolean}
   */
  isRequired(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') return value.trim().length > 0;
    if (Array.isArray(value)) return value.length > 0;
    return true;
  },

  /**
   * Validate numeric input
   * @param {any} value
   * @returns {boolean}
   */
  isNumeric(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
  },

  /**
   * Validate integer
   * @param {any} value
   * @returns {boolean}
   */
  isInteger(value) {
    return Number.isInteger(Number(value));
  },

  /**
   * Validate positive number
   * @param {any} value
   * @returns {boolean}
   */
  isPositive(value) {
    return this.isNumeric(value) && Number(value) > 0;
  },

  /**
   * Validate file type
   * @param {File} file
   * @param {string[]} allowedTypes - e.g., ['image/jpeg', 'image/png']
   * @returns {boolean}
   */
  isFileType(file, allowedTypes) {
    return file && allowedTypes.includes(file.type);
  },

  /**
   * Validate file size
   * @param {File} file
   * @param {number} maxSizeBytes
   * @returns {boolean}
   */
  isFileSize(file, maxSizeBytes) {
    return file && file.size <= maxSizeBytes;
  },

  /**
   * Validate image file
   * @param {File} file
   * @param {number} maxSizeMB - Max size in megabytes
   * @returns {Object} {valid: boolean, error: string}
   */
  validateImageFile(file, maxSizeMB = 10) {
    if (!file) {
      return { valid: false, error: 'No file selected' };
    }

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      return { valid: false, error: 'Please select a JPG, PNG, or WebP image' };
    }

    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      return { valid: false, error: `File size must be less than ${maxSizeMB}MB` };
    }

    return { valid: true, error: null };
  },

  /**
   * Sanitize string (basic XSS prevention)
   * @param {string} str
   * @returns {string}
   */
  sanitizeString(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  /**
   * Sanitize number input
   * @param {any} value
   * @param {number} decimals
   * @returns {number}
   */
  sanitizeNumber(value, decimals = 2) {
    const num = parseFloat(value);
    if (isNaN(num)) return 0;
    return Number(num.toFixed(decimals));
  },

  /**
   * Create validator for form field
   * @param {HTMLElement} field
   * @param {Object} rules
   * @returns {Function}
   */
  createFieldValidator(field, rules) {
    return () => {
      const value = field.value;
      const errors = [];

      if (rules.required && !this.isRequired(value)) {
        errors.push(`${field.name || 'This field'} is required`);
      }

      if (rules.email && value && !this.isEmail(value)) {
        errors.push('Please enter a valid email address');
      }

      if (rules.numeric && value && !this.isNumeric(value)) {
        errors.push('Please enter a valid number');
      }

      if (rules.min !== undefined && value && Number(value) < rules.min) {
        errors.push(`Value must be at least ${rules.min}`);
      }

      if (rules.max !== undefined && value && Number(value) > rules.max) {
        errors.push(`Value must be at most ${rules.max}`);
      }

      if (rules.minLength && value && value.length < rules.minLength) {
        errors.push(`Minimum length is ${rules.minLength} characters`);
      }

      if (rules.maxLength && value && value.length > rules.maxLength) {
        errors.push(`Maximum length is ${rules.maxLength} characters`);
      }

      if (rules.pattern && value && !new RegExp(rules.pattern).test(value)) {
        errors.push(rules.patternMessage || 'Invalid format');
      }

      if (rules.custom && typeof rules.custom === 'function') {
        const customError = rules.custom(value, field);
        if (customError) {
          errors.push(customError);
        }
      }

      // Update field validity
      if (errors.length > 0) {
        field.setCustomValidity(errors[0]);
        return { valid: false, errors };
      } else {
        field.setCustomValidity('');
        return { valid: true, errors: [] };
      }
    };
  },

  /**
   * Validate entire form
   * @param {HTMLFormElement} form
   * @param {Object} fieldRules - Map of field names to validation rules
   * @returns {Object} {valid: boolean, errors: Object}
   */
  validateForm(form, fieldRules = {}) {
    const errors = {};
    let isValid = true;

    // Validate fields with custom rules
    Object.entries(fieldRules).forEach(([fieldName, rules]) => {
      const field = form.elements[fieldName];
      if (field) {
        const validator = this.createFieldValidator(field, rules);
        const result = validator();
        if (!result.valid) {
          errors[fieldName] = result.errors;
          isValid = false;
        }
      }
    });

    // HTML5 validation
    if (!form.checkValidity()) {
      isValid = false;
    }

    return { valid: isValid, errors };
  },

  /**
   * Show validation errors on form
   * @param {HTMLFormElement} form
   * @param {Object} errors - Map of field names to error arrays
   */
  showErrors(form, errors) {
    // Clear existing errors
    form.querySelectorAll('.validation-error').forEach(el => el.remove());

    // Add new errors
    Object.entries(errors).forEach(([fieldName, fieldErrors]) => {
      const field = form.elements[fieldName];
      if (field && fieldErrors.length > 0) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error text-red-600 text-xs mt-1';
        errorDiv.textContent = fieldErrors[0];
        
        field.classList.add('border-red-500');
        field.parentElement.appendChild(errorDiv);
      }
    });
  },

  /**
   * Clear validation errors
   * @param {HTMLFormElement} form
   */
  clearErrors(form) {
    form.querySelectorAll('.validation-error').forEach(el => el.remove());
    form.querySelectorAll('.border-red-500').forEach(el => {
      el.classList.remove('border-red-500');
    });
    
    // Clear custom validity
    Array.from(form.elements).forEach(field => {
      if (field.setCustomValidity) {
        field.setCustomValidity('');
      }
    });
  },
};

export default Validation;
