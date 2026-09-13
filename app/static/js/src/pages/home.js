/**
 * Home Page - Landing page functionality
 */

import API from '../core/api.js';
import UI from '../components/ui.js';
import DOM from '../utils/dom.js';

// Initialize home page
document.addEventListener('DOMContentLoaded', () => {
  console.log('Home page loaded');
  
  // Any home-specific functionality goes here
  initHeroAnimations();
});

/**
 * Initialize hero section animations
 */
function initHeroAnimations() {
  const hero = DOM.qs('.hero');
  if (!hero) return;
  
  // Add fade-in animation
  hero.classList.add('animate-fade-in');
}

export default {};
