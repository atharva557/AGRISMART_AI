/**
 * Notification System - Toast notifications
 */

import { DOM } from '../utils/dom.js';

class NotificationManager {
  constructor() {
    this.container = null;
    this.notifications = [];
    this.maxNotifications = 5;
    this.init();
  }

  /**
   * Initialize notification container
   */
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'fixed bottom-4 right-4 z-[1060] flex flex-col gap-3 max-w-md';
      this.container.setAttribute('aria-live', 'polite');
      this.container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(this.container);
    }
  }

  /**
   * Show notification
   * @param {string} message - Notification message
   * @param {string} type - Notification type (success, error, warning, info)
   * @param {number} duration - Duration in ms (0 = permanent)
   * @returns {Object} Notification object with close method
   */
  show(message, type = 'info', duration = 4000) {
    // Remove oldest if at max
    if (this.notifications.length >= this.maxNotifications) {
      const oldest = this.notifications[0];
      oldest.close();
    }

    const notification = this.createNotification(message, type, duration);
    this.notifications.push(notification);
    
    return notification;
  }

  /**
   * Create notification element
   * @param {string} message
   * @param {string} type
   * @param {number} duration
   * @returns {Object}
   */
  createNotification(message, type, duration) {
    const icons = {
      success: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>`,
      error: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>`,
      warning: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`,
      info: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>`,
    };

    const typeClasses = {
      success: 'bg-green-50 text-green-900 border-green-200',
      error: 'bg-red-50 text-red-900 border-red-200',
      warning: 'bg-yellow-50 text-yellow-900 border-yellow-200',
      info: 'bg-blue-50 text-blue-900 border-blue-200',
    };

    const element = document.createElement('div');
    element.className = `flex items-start gap-3 p-4 rounded-lg border shadow-lg ${typeClasses[type]} animate-slide-down`;
    element.setAttribute('role', 'alert');
    element.innerHTML = `
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${icons[type] || icons.info}
      </svg>
      <div class="flex-1 text-sm">${DOM.escapeHtml(message)}</div>
      <button class="notification-close p-1 hover:bg-black/5 rounded transition-colors" 
              aria-label="Close notification">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    `;

    const notification = {
      element,
      type,
      message,
      timer: null,
      close: () => this.closeNotification(notification),
    };

    // Close button
    const closeBtn = element.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => notification.close());

    // Auto-close after duration
    if (duration > 0) {
      notification.timer = setTimeout(() => notification.close(), duration);
    }

    // Add progress bar for timed notifications
    if (duration > 0) {
      const progress = document.createElement('div');
      progress.className = 'absolute bottom-0 left-0 right-0 h-1 bg-current opacity-20 rounded-b-lg';
      progress.style.animation = `shrink ${duration}ms linear`;
      element.style.position = 'relative';
      element.appendChild(progress);
    }

    this.container.appendChild(element);
    
    return notification;
  }

  /**
   * Close notification
   * @param {Object} notification
   */
  closeNotification(notification) {
    if (notification.timer) {
      clearTimeout(notification.timer);
    }

    notification.element.style.animation = 'fadeOut 0.3s ease-out';
    
    setTimeout(() => {
      notification.element.remove();
      
      const index = this.notifications.indexOf(notification);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    }, 300);
  }

  /**
   * Clear all notifications
   */
  clearAll() {
    this.notifications.forEach(notification => notification.close());
    this.notifications = [];
  }

  /**
   * Success notification
   * @param {string} message
   * @param {number} duration
   */
  success(message, duration = 4000) {
    return this.show(message, 'success', duration);
  }

  /**
   * Error notification
   * @param {string} message
   * @param {number} duration
   */
  error(message, duration = 5000) {
    return this.show(message, 'error', duration);
  }

  /**
   * Warning notification
   * @param {string} message
   * @param {number} duration
   */
  warning(message, duration = 4000) {
    return this.show(message, 'warning', duration);
  }

  /**
   * Info notification
   * @param {string} message
   * @param {number} duration
   */
  info(message, duration = 4000) {
    return this.show(message, 'info', duration);
  }
}

// Create singleton instance
const Notification = new NotificationManager();

// Add keyframe animation for progress bar
const style = document.createElement('style');
style.textContent = `
  @keyframes shrink {
    from { transform: scaleX(1); transform-origin: left; }
    to { transform: scaleX(0); transform-origin: left; }
  }
  
  @keyframes fadeOut {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(-10px); }
  }
`;
document.head.appendChild(style);

export { Notification, NotificationManager };
export default Notification;
