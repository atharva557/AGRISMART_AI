/**
 * Form Components - Reusable form handling
 */

import { DOM } from '../utils/dom.js';
import UI from './ui.js';

export class FormHandler {
  constructor(formElement) {
    this.form = formElement;
    this.isSubmitting = false;
  }

  /**
   * Get form data as object
   * @returns {Object}
   */
  getData() {
    const formData = new FormData(this.form);
    const data = {};
    
    for (const [key, value] of formData) {
      // Handle checkboxes and multiple selects
      if (data[key]) {
        if (!Array.isArray(data[key])) {
          data[key] = [data[key]];
        }
        data[key].push(value);
      } else {
        data[key] = value;
      }
    }
    
    return data;
  }

  /**
   * Get numeric value from form
   * @param {string} name - Field name
   * @returns {number}
   */
  getNumber(name) {
    return Number(new FormData(this.form).get(name));
  }

  /**
   * Set form values
   * @param {Object} data - Data to populate
   */
  setData(data) {
    Object.entries(data).forEach(([key, value]) => {
      const field = this.form.elements[key];
      if (field) {
        if (field.type === 'checkbox') {
          field.checked = Boolean(value);
        } else if (field.type === 'radio') {
          const radio = this.form.querySelector(`input[name="${key}"][value="${value}"]`);
          if (radio) radio.checked = true;
        } else {
          field.value = value;
        }
      }
    });
  }

  /**
   * Validate form
   * @returns {boolean}
   */
  validate() {
    return this.form.reportValidity();
  }

  /**
   * Reset form
   */
  reset() {
    this.form.reset();
  }

  /**
   * Disable form
   */
  disable() {
    const elements = this.form.elements;
    for (let i = 0; i < elements.length; i++) {
      elements[i].disabled = true;
    }
  }

  /**
   * Enable form
   */
  enable() {
    const elements = this.form.elements;
    for (let i = 0; i < elements.length; i++) {
      elements[i].disabled = false;
    }
  }

  /**
   * Handle form submission
   * @param {Function} handler - Async submission handler
   * @param {HTMLElement} outputContainer - Optional output container
   */
  async onSubmit(handler, outputContainer = null) {
    this.form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (this.isSubmitting) return;
      if (!this.validate()) return;
      
      this.isSubmitting = true;
      this.disable();
      
      if (outputContainer) {
        UI.showLoading(outputContainer, 'Processing...');
      }
      
      try {
        const result = await handler(this.getData());
        
        if (outputContainer && result) {
          if (result.success) {
            UI.showSuccess(outputContainer, result.message || 'Success');
          } else {
            UI.showError(outputContainer, result.message || 'An error occurred');
          }
        }
        
        return result;
      } catch (error) {
        console.error('Form submission error:', error);
        
        if (outputContainer) {
          UI.showError(outputContainer, 'An unexpected error occurred. Please try again.');
        }
        
        throw error;
      } finally {
        this.isSubmitting = false;
        this.enable();
      }
    });
  }
}

/**
 * Create form handler
 * @param {string|HTMLElement} formSelector - Form element or selector
 * @returns {FormHandler}
 */
export function createFormHandler(formSelector) {
  const form = typeof formSelector === 'string' 
    ? DOM.qs(formSelector) 
    : formSelector;
    
  if (!form) {
    throw new Error(`Form not found: ${formSelector}`);
  }
  
  return new FormHandler(form);
}

export default FormHandler;
