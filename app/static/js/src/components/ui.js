/**
 * UI Components - Reusable UI state management
 */

import { DOM } from '../utils/dom.js';

export const UI = {
  /**
   * Show loading state
   * @param {HTMLElement} container - Container element
   * @param {string} message - Loading message
   */
  showLoading(container, message = 'Loading...') {
    if (!container) return;
    
    container.classList.add('relative');
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="spinner"></div>
      <p class="loading-text text-sm text-gray-600 mt-4">${DOM.escapeHtml(message)}</p>
    `;
    
    // Remove any existing loading overlay
    const existing = container.querySelector('.loading-overlay');
    if (existing) {
      existing.remove();
    }
    
    container.appendChild(overlay);
  },

  /**
   * Hide loading state
   * @param {HTMLElement} container - Container element
   */
  hideLoading(container) {
    if (!container) return;
    
    const overlay = container.querySelector('.loading-overlay');
    if (overlay) {
      overlay.remove();
    }
    
    container.classList.remove('relative');
  },

  /**
   * Show alert message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Message text
   * @param {string} type - Alert type (success, error, warning, info)
   * @param {string} title - Alert title (optional)
   */
  showAlert(container, message, type = 'info', title = null) {
    if (!container) return;
    
    const icons = {
      success: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
      error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
      warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>',
      info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
    };
    
    this.hideLoading(container);
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${icons[type] || icons.info}
      </svg>
      <div class="alert-content flex-1">
        ${title ? `<div class="alert-title font-bold mb-1">${DOM.escapeHtml(title)}</div>` : ''}
        <p class="alert-message">${DOM.escapeHtml(message)}</p>
      </div>
    `;
    
    container.innerHTML = '';
    container.appendChild(alert);
  },

  /**
   * Show success message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Success message
   * @param {string} title - Success title (optional)
   */
  showSuccess(container, message, title = 'Success') {
    this.showAlert(container, message, 'success', title);
  },

  /**
   * Show error message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Error message
   * @param {string} title - Error title (optional)
   */
  showError(container, message, title = 'Error') {
    this.showAlert(container, message, 'error', title);
  },

  /**
   * Show warning message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Warning message
   * @param {string} title - Warning title (optional)
   */
  showWarning(container, message, title = 'Warning') {
    this.showAlert(container, message, 'warning', title);
  },

  /**
   * Show info message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Info message
   * @param {string} title - Info title (optional)
   */
  showInfo(container, message, title = 'Information') {
    this.showAlert(container, message, 'info', title);
  },

  /**
   * Show toast notification
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {number} duration - Duration in ms (default: 3000)
   */
  toast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fixed bottom-4 right-4 z-50 max-w-md shadow-xl animate-fade-in`;
    toast.style.animation = 'slideDown 0.3s ease-out';
    toast.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div class="alert-content">
        <p class="alert-message">${DOM.escapeHtml(message)}</p>
      </div>
      <button class="ml-auto hover:opacity-70" aria-label="Close">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    `;
    
    // Close button handler
    const closeBtn = toast.querySelector('button');
    closeBtn.addEventListener('click', () => {
      toast.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    });
    
    document.body.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
      toast.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  /**
   * Clear container
   * @param {HTMLElement} container - Container element
   */
  clear(container) {
    if (!container) return;
    container.innerHTML = '';
  },

  /**
   * Toggle element visibility
   * @param {HTMLElement} element - Element to toggle
   * @param {boolean} show - Force show/hide (optional)
   */
  toggle(element, show = null) {
    if (!element) return;
    
    if (show === null) {
      element.classList.toggle('hidden');
    } else {
      element.classList.toggle('hidden', !show);
    }
  },

  /**
   * Show element
   * @param {HTMLElement} element - Element to show
   */
  show(element) {
    if (!element) return;
    element.classList.remove('hidden');
    element.setAttribute('aria-hidden', 'false');
  },

  /**
   * Hide element
   * @param {HTMLElement} element - Element to hide
   */
  hide(element) {
    if (!element) return;
    element.classList.add('hidden');
    element.setAttribute('aria-hidden', 'true');
  },

  /**
   * Disable element
   * @param {HTMLElement} element - Element to disable
   */
  disable(element) {
    if (!element) return;
    element.disabled = true;
    element.setAttribute('aria-disabled', 'true');
  },

  /**
   * Enable element
   * @param {HTMLElement} element - Element to enable
   */
  enable(element) {
    if (!element) return;
    element.disabled = false;
    element.setAttribute('aria-disabled', 'false');
  },

  /**
   * Confirm dialog
   * @param {string} message - Confirmation message
   * @param {string} title - Dialog title
   * @returns {Promise<boolean>}
   */
  async confirm(message, title = 'Confirm') {
    return new Promise((resolve) => {
      const backdrop = document.createElement('div');
      backdrop.className = 'fixed inset-0 bg-black/50 z-[1040] animate-fade-in';
      
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 flex items-center justify-center z-[1050] p-4';
      modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-2xl max-w-md w-full animate-slide-down">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-bold text-gray-900">${DOM.escapeHtml(title)}</h3>
          </div>
          <div class="p-6">
            <p class="text-gray-700">${DOM.escapeHtml(message)}</p>
          </div>
          <div class="p-6 border-t border-gray-200 flex gap-3 justify-end">
            <button class="btn btn-secondary" data-action="cancel">Cancel</button>
            <button class="btn btn-primary" data-action="confirm">Confirm</button>
          </div>
        </div>
      `;
      
      const cleanup = () => {
        backdrop.remove();
        modal.remove();
      };
      
      modal.querySelector('[data-action="cancel"]').addEventListener('click', () => {
        cleanup();
        resolve(false);
      });
      
      modal.querySelector('[data-action="confirm"]').addEventListener('click', () => {
        cleanup();
        resolve(true);
      });
      
      backdrop.addEventListener('click', () => {
        cleanup();
        resolve(false);
      });
      
      document.body.appendChild(backdrop);
      document.body.appendChild(modal);
    });
  },

  /**
   * Set active navigation item
   * @param {string} path - Current path
   */
  setActiveNav(path) {
    const navLinks = document.querySelectorAll('[data-nav-link]');
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === path || (path !== '/' && href.startsWith(path))) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.classList.remove('active');
        link.removeAttribute('aria-current');
      }
    });
  },

  /**
   * Scroll to top smoothly
   */
  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },
};

export default UI;
