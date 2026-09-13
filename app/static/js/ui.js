/**
 * AgriSmart AI - UI State Management
 * Handle loading, error, success states and UI updates
 */

const UI = {
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
      <p class="loading-text">${Utils.escapeHtml(message)}</p>
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
   * Show error message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Error message
   * @param {string} title - Error title (optional)
   */
  showError(container, message, title = 'Error') {
    if (!container) return;
    
    this.hideLoading(container);
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div class="alert-content">
        <div class="alert-title">${Utils.escapeHtml(title)}</div>
        <p class="alert-message">${Utils.escapeHtml(message)}</p>
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
    if (!container) return;
    
    this.hideLoading(container);
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div class="alert-content">
        <div class="alert-title">${Utils.escapeHtml(title)}</div>
        <p class="alert-message">${Utils.escapeHtml(message)}</p>
      </div>
    `;
    
    container.innerHTML = '';
    container.appendChild(alert);
  },

  /**
   * Show warning message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Warning message
   * @param {string} title - Warning title (optional)
   */
  showWarning(container, message, title = 'Warning') {
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
      </svg>
      <div class="alert-content">
        <div class="alert-title">${Utils.escapeHtml(title)}</div>
        <p class="alert-message">${Utils.escapeHtml(message)}</p>
      </div>
    `;
    
    container.appendChild(alert);
  },

  /**
   * Show info message
   * @param {HTMLElement} container - Container element
   * @param {string} message - Info message
   * @param {string} title - Info title (optional)
   */
  showInfo(container, message, title = 'Information') {
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-info';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div class="alert-content">
        <div class="alert-title">${Utils.escapeHtml(title)}</div>
        <p class="alert-message">${Utils.escapeHtml(message)}</p>
      </div>
    `;
    
    container.appendChild(alert);
  },

  /**
   * Show empty state
   * @param {HTMLElement} container - Container element
   * @param {string} message - Empty state message
   * @param {string} title - Empty state title
   */
  showEmpty(container, message, title = 'No Data') {
    if (!container) return;
    
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    emptyState.innerHTML = `
      <svg class="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
      </svg>
      <h3 class="empty-state-title">${Utils.escapeHtml(title)}</h3>
      <p class="empty-state-message">${Utils.escapeHtml(message)}</p>
    `;
    
    container.innerHTML = '';
    container.appendChild(emptyState);
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
   * Add CSS class
   * @param {HTMLElement} element - Element
   * @param {string} className - Class name
   */
  addClass(element, className) {
    if (!element) return;
    element.classList.add(className);
  },

  /**
   * Remove CSS class
   * @param {HTMLElement} element - Element
   * @param {string} className - Class name
   */
  removeClass(element, className) {
    if (!element) return;
    element.classList.remove(className);
  },

  /**
   * Toggle CSS class
   * @param {HTMLElement} element - Element
   * @param {string} className - Class name
   */
  toggleClass(element, className) {
    if (!element) return;
    element.classList.toggle(className);
  },

  /**
   * Show toast notification
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {number} duration - Duration in ms (default: 3000)
   */
  toast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fixed bottom-4 right-4 z-50 max-w-md animate-fade-in`;
    toast.style.animation = 'slideDown 0.3s ease-out';
    toast.innerHTML = `
      <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div class="alert-content">
        <p class="alert-message">${Utils.escapeHtml(message)}</p>
      </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    }, duration);
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
      backdrop.className = 'modal-backdrop';
      
      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.innerHTML = `
        <div class="modal-header">
          <h3 class="modal-title">${Utils.escapeHtml(title)}</h3>
        </div>
        <div class="modal-body">
          <p>${Utils.escapeHtml(message)}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-action="cancel">Cancel</button>
          <button class="btn btn-primary" data-action="confirm">Confirm</button>
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
   * Scroll to top smoothly
   */
  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
  }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Set active navigation based on current path
  UI.setActiveNav(window.location.pathname);
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = UI;
}
