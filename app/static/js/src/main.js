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

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  console.log('AgriSmart AI - Main module loaded');
  
  // Set active navigation
  UI.setActiveNav(window.location.pathname);
  
  // Check backend health
  await checkBackendHealth();
  
  // Initialize common features
  initAccessibility();
  initMobileMenu();
});

/**
 * Check backend health and update indicators
 */
async function checkBackendHealth() {
  const indicators = [
    DOM.byId('health-indicator'),
    DOM.byId('hero-health-indicator')
  ];
  
  const textElements = [
    DOM.byId('health-text'),
    DOM.byId('hero-health-text')
  ];
  
  try {
    const isHealthy = await API.checkHealth();
    
    indicators.forEach(indicator => {
      if (!indicator) return;
      
      if (isHealthy) {
        indicator.classList.remove('bg-gray-300', 'animate-pulse');
        indicator.classList.add('bg-green-400');
        indicator.title = 'System operational';
      } else {
        indicator.classList.remove('bg-gray-300', 'animate-pulse');
        indicator.classList.add('bg-red-500');
        indicator.title = 'System unavailable';
      }
    });
    
    textElements.forEach(textEl => {
      if (!textEl) return;
      
      if (isHealthy) {
        textEl.textContent = 'System ready';
      } else {
        textEl.textContent = 'Backend unavailable';
      }
    });
  } catch (error) {
    console.error('Health check failed:', error);
    
    indicators.forEach(indicator => {
      if (indicator) {
        indicator.classList.remove('animate-pulse');
        indicator.classList.add('bg-yellow-500');
      }
    });
    
    textElements.forEach(textEl => {
      if (textEl) {
        textEl.textContent = 'Status unknown';
      }
    });
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
  
  // Keyboard navigation for mobile menu toggle
  const mobileMenuToggle = DOM.byId('mobile-menu-toggle');
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        mobileMenuToggle.click();
      }
    });
  }
  
  // Add focus visible class for keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-nav');
    }
  });
  
  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
  });
}

/**
 * Initialize mobile menu
 */
function initMobileMenu() {
  const menuToggle = DOM.byId('mobile-menu-toggle');
  const mobileMenu = DOM.byId('mobile-menu');
  
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.contains('hidden');
      
      if (isOpen) {
        mobileMenu.classList.remove('hidden');
        menuToggle.setAttribute('aria-expanded', 'true');
      } else {
        mobileMenu.classList.add('hidden');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });
    
    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });
    
    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenu.contains(e.target) && 
          !menuToggle.contains(e.target) && 
          !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }
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
  checkBackendHealth 
};
