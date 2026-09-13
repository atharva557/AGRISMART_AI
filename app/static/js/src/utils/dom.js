/**
 * DOM Utilities
 * Helper functions for DOM manipulation
 */

export const DOM = {
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
   * Check if device is mobile
   * @returns {boolean}
   */
  isMobile() {
    return window.innerWidth < 768;
  },
};

export default DOM;
