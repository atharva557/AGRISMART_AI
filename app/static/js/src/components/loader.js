/**
 * LeafLoader Component
 * Professional loading indicator with spinning leaf animation
 * Works in both Light and Dark modes
 */

class LeafLoader {
  /**
   * Create a leaf loader element
   * @param {string} text - Optional loading text
   * @returns {HTMLElement} Loader element
   */
  static create(text = 'Processing...') {
    const loader = document.createElement('div');
    loader.className = 'leaf-loader';
    loader.setAttribute('role', 'status');
    loader.setAttribute('aria-live', 'polite');
    loader.setAttribute('aria-label', text);

    loader.innerHTML = `
      <svg class="leaf-loader__icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M12 2C11 2 10 2.5 9.5 3.5C9 4.5 9 5.5 9 6.5C9 8 10 9 11 10C10 11 9 13 9 15C9 17 10 19 12 22C14 19 15 17 15 15C15 13 14 11 13 10C14 9 15 8 15 6.5C15 5.5 15 4.5 14.5 3.5C14 2.5 13 2 12 2Z" 
              fill="currentColor" opacity="0.9"/>
        <circle cx="12" cy="6" r="1.5" fill="currentColor" opacity="0.3"/>
        <path d="M11 10C10.5 10.5 9.5 11.5 9 13C8.8 13.5 9 14 9 14.5C9.2 15 9.5 15.3 10 15.5" 
              stroke="currentColor" stroke-width="0.8" opacity="0.6" stroke-linecap="round"/>
      </svg>
      <span class="leaf-loader__text">${this.escapeHtml(text)}</span>
    `;

    return loader;
  }

  /**
   * Show loader in a container
   * @param {HTMLElement|string} container - Container element or selector
   * @param {string} text - Optional loading text
   * @returns {HTMLElement} Loader element
   */
  static show(container, text = 'Processing...') {
    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) {
      console.warn('LeafLoader: Container not found');
      return null;
    }

    // Remove any existing loader
    this.hide(element);

    const loader = this.create(text);
    loader.dataset.leafLoader = 'true';
    element.appendChild(loader);

    return loader;
  }

  /**
   * Hide loader in a container
   * @param {HTMLElement|string} container - Container element or selector
   */
  static hide(container) {
    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) return;

    const loaders = element.querySelectorAll('[data-leaf-loader="true"]');
    loaders.forEach(loader => loader.remove());
  }

  /**
   * Show loader as overlay over an element
   * @param {HTMLElement|string} container - Container element or selector
   * @param {string} text - Optional loading text
   * @returns {HTMLElement} Overlay element
   */
  static showOverlay(container, text = 'Processing...') {
    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) {
      console.warn('LeafLoader: Container not found');
      return null;
    }

    // Remove any existing overlay
    this.hideOverlay(element);

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.dataset.leafLoaderOverlay = 'true';

    const loader = this.create(text);
    overlay.appendChild(loader);

    // Ensure container has position context
    const position = window.getComputedStyle(element).position;
    if (position === 'static') {
      element.style.position = 'relative';
    }

    element.appendChild(overlay);

    return overlay;
  }

  /**
   * Hide overlay loader in a container
   * @param {HTMLElement|string} container - Container element or selector
   */
  static hideOverlay(container) {
    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) return;

    const overlays = element.querySelectorAll('[data-leaf-loader-overlay="true"]');
    overlays.forEach(overlay => overlay.remove());
  }

  /**
   * Set button loading state
   * @param {HTMLElement|string} button - Button element or selector
   * @param {boolean} loading - Loading state
   */
  static setButtonLoading(button, loading) {
    const element = typeof button === 'string' 
      ? document.querySelector(button) 
      : button;

    if (!element) return;

    if (loading) {
      element.classList.add('loading');
      element.disabled = true;
      element.setAttribute('aria-busy', 'true');
      // Store original text
      element.dataset.originalText = element.textContent;
    } else {
      element.classList.remove('loading');
      element.disabled = false;
      element.removeAttribute('aria-busy');
      // Restore original text if stored
      if (element.dataset.originalText) {
        element.textContent = element.dataset.originalText;
        delete element.dataset.originalText;
      }
    }
  }

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Create inline loader (smaller, for inline use)
   * @param {string} text - Optional loading text
   * @returns {HTMLElement} Inline loader element
   */
  static createInline(text = 'Loading...') {
    const loader = document.createElement('span');
    loader.className = 'inline-flex items-center gap-2';
    loader.setAttribute('role', 'status');
    loader.setAttribute('aria-label', text);

    loader.innerHTML = `
      <svg class="w-4 h-4 animate-spin" style="color: var(--primary);" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M12 2C11 2 10 2.5 9.5 3.5C9 4.5 9 5.5 9 6.5C9 8 10 9 11 10C10 11 9 13 9 15C9 17 10 19 12 22C14 19 15 17 15 15C15 13 14 11 13 10C14 9 15 8 15 6.5C15 5.5 15 4.5 14.5 3.5C14 2.5 13 2 12 2Z" 
              fill="currentColor" opacity="0.9"/>
      </svg>
      <span class="text-sm" style="color: var(--text-muted);">${this.escapeHtml(text)}</span>
    `;

    return loader;
  }
}

// Export for ES modules
export default LeafLoader;

// Also attach to window for backward compatibility
if (typeof window !== 'undefined') {
  window.LeafLoader = LeafLoader;
}
