/**
 * AgriSmart AI - Form Validation
 * Comprehensive form validation with real-time feedback
 */

const Validator = {
  /**
   * Validation rules
   */
  rules: {
    required: (value) => {
      return value !== null && value !== '' && value !== undefined;
    },

    number: (value) => {
      return !isNaN(parseFloat(value)) && isFinite(value);
    },

    integer: (value) => {
      return Number.isInteger(Number(value));
    },

    range: (value, min, max) => {
      const num = parseFloat(value);
      return num >= min && num <= max;
    },

    min: (value, min) => {
      return parseFloat(value) >= min;
    },

    max: (value, max) => {
      return parseFloat(value) <= max;
    },

    email: (value) => {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(value);
    },

    fileType: (file, types) => {
      if (!file) return false;
      return types.includes(file.type);
    },

    fileSize: (file, maxSizeBytes) => {
      if (!file) return false;
      return file.size <= maxSizeBytes;
    },

    minLength: (value, length) => {
      return value && value.length >= length;
    },

    maxLength: (value, length) => {
      return value && value.length <= length;
    },

    pattern: (value, pattern) => {
      const regex = new RegExp(pattern);
      return regex.test(value);
    }
  },

  /**
   * Error messages
   */
  messages: {
    required: 'This field is required',
    number: 'Please enter a valid number',
    integer: 'Please enter a whole number',
    range: (min, max) => `Value must be between ${min} and ${max}`,
    min: (min) => `Value must be at least ${min}`,
    max: (max) => `Value must be at most ${max}`,
    email: 'Please enter a valid email address',
    fileType: (types) => `Allowed file types: ${types.join(', ')}`,
    fileSize: (size) => `File size must not exceed ${Utils.formatFileSize(size)}`,
    minLength: (length) => `Minimum ${length} characters required`,
    maxLength: (length) => `Maximum ${length} characters allowed`,
    pattern: 'Invalid format'
  },

  /**
   * Validate a single field
   * @param {HTMLElement} field - Input field
   * @param {Object} rules - Validation rules
   * @returns {Object} - { valid: boolean, errors: Array }
   */
  validateField(field, rules = {}) {
    const errors = [];
    const value = field.value;
    const fieldName = field.getAttribute('name') || 'Field';

    // Required check
    if (rules.required && !this.rules.required(value)) {
      errors.push(this.messages.required);
      return { valid: false, errors };
    }

    // Skip other validations if field is empty and not required
    if (!rules.required && !value) {
      return { valid: true, errors: [] };
    }

    // Number validation
    if (rules.number && !this.rules.number(value)) {
      errors.push(this.messages.number);
    }

    // Integer validation
    if (rules.integer && !this.rules.integer(value)) {
      errors.push(this.messages.integer);
    }

    // Range validation
    if (rules.range && !this.rules.range(value, rules.range.min, rules.range.max)) {
      errors.push(this.messages.range(rules.range.min, rules.range.max));
    }

    // Min validation
    if (rules.min !== undefined && !this.rules.min(value, rules.min)) {
      errors.push(this.messages.min(rules.min));
    }

    // Max validation
    if (rules.max !== undefined && !this.rules.max(value, rules.max)) {
      errors.push(this.messages.max(rules.max));
    }

    // Email validation
    if (rules.email && !this.rules.email(value)) {
      errors.push(this.messages.email);
    }

    // Min length validation
    if (rules.minLength && !this.rules.minLength(value, rules.minLength)) {
      errors.push(this.messages.minLength(rules.minLength));
    }

    // Max length validation
    if (rules.maxLength && !this.rules.maxLength(value, rules.maxLength)) {
      errors.push(this.messages.maxLength(rules.maxLength));
    }

    // Pattern validation
    if (rules.pattern && !this.rules.pattern(value, rules.pattern)) {
      errors.push(rules.patternMessage || this.messages.pattern);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  },

  /**
   * Validate a file input
   * @param {HTMLElement} input - File input
   * @param {Object} rules - Validation rules
   * @returns {Object} - { valid: boolean, errors: Array }
   */
  validateFile(input, rules = {}) {
    const errors = [];
    const file = input.files[0];

    // Required check
    if (rules.required && !file) {
      errors.push('Please select a file');
      return { valid: false, errors };
    }

    if (!file) {
      return { valid: true, errors: [] };
    }

    // File type validation
    if (rules.fileTypes && !this.rules.fileType(file, rules.fileTypes)) {
      errors.push(this.messages.fileType(rules.fileTypes));
    }

    // File size validation
    if (rules.maxSize && !this.rules.fileSize(file, rules.maxSize)) {
      errors.push(this.messages.fileSize(rules.maxSize));
    }

    return {
      valid: errors.length === 0,
      errors
    };
  },

  /**
   * Validate entire form
   * @param {HTMLFormElement} form - Form element
   * @param {Object} fieldRules - Rules for each field
   * @returns {Object} - { valid: boolean, errors: Object }
   */
  validateForm(form, fieldRules = {}) {
    const allErrors = {};
    let isValid = true;

    Object.keys(fieldRules).forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (!field) return;

      const rules = fieldRules[fieldName];
      const validation = field.type === 'file' 
        ? this.validateFile(field, rules)
        : this.validateField(field, rules);

      if (!validation.valid) {
        isValid = false;
        allErrors[fieldName] = validation.errors;
      }
    });

    return {
      valid: isValid,
      errors: allErrors
    };
  },

  /**
   * Show field error
   * @param {HTMLElement} field - Input field
   * @param {Array} errors - Error messages
   */
  showFieldError(field, errors) {
    if (!field) return;

    // Add error class
    field.classList.add('input-error');

    // Find or create error container
    let errorContainer = field.parentElement.querySelector('.input-error-message');
    
    if (!errorContainer) {
      errorContainer = document.createElement('span');
      errorContainer.className = 'input-error-message';
      field.parentElement.appendChild(errorContainer);
    }

    // Show error message
    errorContainer.textContent = errors[0]; // Show first error
    errorContainer.style.display = 'block';

    // Set aria-invalid
    field.setAttribute('aria-invalid', 'true');
  },

  /**
   * Clear field error
   * @param {HTMLElement} field - Input field
   */
  clearFieldError(field) {
    if (!field) return;

    // Remove error class
    field.classList.remove('input-error');

    // Remove error message
    const errorContainer = field.parentElement.querySelector('.input-error-message');
    if (errorContainer) {
      errorContainer.remove();
    }

    // Remove aria-invalid
    field.removeAttribute('aria-invalid');
  },

  /**
   * Show all form errors
   * @param {HTMLFormElement} form - Form element
   * @param {Object} errors - Errors object
   */
  showFormErrors(form, errors) {
    Object.keys(errors).forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (field) {
        this.showFieldError(field, errors[fieldName]);
      }
    });
  },

  /**
   * Clear all form errors
   * @param {HTMLFormElement} form - Form element
   */
  clearFormErrors(form) {
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => this.clearFieldError(field));
  },

  /**
   * Setup real-time validation for a field
   * @param {HTMLElement} field - Input field
   * @param {Object} rules - Validation rules
   * @param {Function} onChange - Optional callback
   */
  setupRealtimeValidation(field, rules, onChange = null) {
    if (!field) return;

    const validate = Utils.debounce(() => {
      const validation = field.type === 'file'
        ? this.validateFile(field, rules)
        : this.validateField(field, rules);

      if (!validation.valid) {
        this.showFieldError(field, validation.errors);
      } else {
        this.clearFieldError(field);
      }

      if (onChange) {
        onChange(validation);
      }
    }, 300);

    // Validate on input/change
    field.addEventListener('input', validate);
    field.addEventListener('change', validate);
    field.addEventListener('blur', validate);
  },

  /**
   * Setup form validation
   * @param {HTMLFormElement} form - Form element
   * @param {Object} fieldRules - Rules for each field
   * @param {Function} onSubmit - Submit callback
   * @returns {Function} - Cleanup function
   */
  setupFormValidation(form, fieldRules, onSubmit) {
    if (!form) return () => {};

    const handleSubmit = (e) => {
      e.preventDefault();

      // Clear previous errors
      this.clearFormErrors(form);

      // Validate form
      const validation = this.validateForm(form, fieldRules);

      if (!validation.valid) {
        // Show errors
        this.showFormErrors(form, validation.errors);

        // Focus first error field
        const firstErrorField = Object.keys(validation.errors)[0];
        const field = form.querySelector(`[name="${firstErrorField}"]`);
        if (field) field.focus();

        return;
      }

      // Form is valid, call submit callback
      if (onSubmit) {
        onSubmit(new FormData(form));
      }
    };

    form.addEventListener('submit', handleSubmit);

    // Setup realtime validation for each field
    Object.keys(fieldRules).forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (field) {
        this.setupRealtimeValidation(field, fieldRules[fieldName]);
      }
    });

    // Return cleanup function
    return () => {
      form.removeEventListener('submit', handleSubmit);
    };
  },

  /**
   * Get form data as object
   * @param {HTMLFormElement} form - Form element
   * @returns {Object}
   */
  getFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (const [key, value] of formData) {
      // Handle multiple values (checkboxes, multi-select)
      if (data[key]) {
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    }

    return data;
  }
};

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Validator;
}
