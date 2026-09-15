/**
 * AgriSmart AI - Main JavaScript Entry Point
 * Loaded on all pages
 */

import API from './core/api.js';
import UI from './components/ui.js';
import DOM from './utils/dom.js';
import { Format } from './utils/format.js';
import { Helpers } from './utils/helpers.js';
import { Validation } from './utils/validation.js';
import { FormHandler, createFormHandler } from './components/form.js';
import { Modal, confirm, alert } from './components/modal.js';
import Notification from './components/notification.js';
import LeafLoader from './components/loader.js';
import I18n from './utils/i18n.js';

// Make modules globally available for backward compatibility
window.API = API;
window.UI = UI;
window.DOM = DOM;
window.Format = Format;
window.Helpers = Helpers;
window.Validation = Validation;
window.FormHandler = FormHandler;
window.createFormHandler = createFormHandler;
window.Modal = Modal;
window.modalConfirm = confirm;
window.modalAlert = alert;
window.Notification = Notification;
window.LeafLoader = LeafLoader;
window.I18n = I18n;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize instant client-side translation
  I18n.init();

  // Silently check backend health (no visible status UI)
  checkBackendHealth();

  // Initialize accessibility features
  initAccessibility();

  // Initialize background page prefetching for instant page navigation
  initPagePrefetch();
});

/**
 * Prefetch internal pages on hover/idle for instant loading
 */
function initPagePrefetch() {
  const prefetched = new Set();

  function prefetchUrl(url) {
    if (!url || prefetched.has(url) || url.startsWith('#') || url.includes('://')) return;
    prefetched.add(url);

    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  }

  // Preload primary route HTML in background after initial page settles
  const coreRoutes = ['/', '/disease', '/advisory', '/about'];
  setTimeout(() => {
    coreRoutes.forEach(route => {
      if (route !== window.location.pathname) {
        prefetchUrl(route);
      }
    });
  }, 1200);

  // Instant prefetch on link hover or touch
  document.addEventListener('mouseover', (e) => {
    const anchor = e.target.closest('a[href^="/"]');
    if (anchor && anchor.getAttribute('href')) {
      prefetchUrl(anchor.getAttribute('href'));
    }
  }, { passive: true });

  document.addEventListener('touchstart', (e) => {
    const anchor = e.target.closest('a[href^="/"]');
    if (anchor && anchor.getAttribute('href')) {
      prefetchUrl(anchor.getAttribute('href'));
    }
  }, { passive: true });
}

/**
 * Check backend health — silent check, no UI status text shown.
 * Logs result to console only.
 */
async function checkBackendHealth() {
  try {
    const isHealthy = await API.checkHealth();
    if (!isHealthy) {
      console.warn('AgriSmart AI: backend health check returned unhealthy.');
    }
  } catch (error) {
    console.error('AgriSmart AI: health check failed:', error);
  }
}

/**
 * Initialize accessibility features
 */
function initAccessibility() {
  // Skip link functionality
  const skipLink = DOM.qs('.skip-link');
  if (skipLink) {
    skipLink.addEventListener('click', (e) => {
      e.preventDefault();
      const mainContent = DOM.byId('main-content') || DOM.qs('main');
      if (mainContent) {
        mainContent.focus();
        mainContent.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  // Add keyboard-nav class for focus-visible enhancements
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-nav');
    }
  });

  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
  });
}

// Export for testing and module usage
export {
  API,
  UI,
  DOM,
  Format,
  Helpers,
  Validation,
  FormHandler,
  createFormHandler,
  Modal,
  confirm,
  alert,
  Notification,
  LeafLoader,
  checkBackendHealth
};
