/**
 * Modal Component - Reusable modal dialogs
 */

import { DOM } from '../utils/dom.js';

export class Modal {
  constructor(options = {}) {
    this.title = options.title || 'Modal';
    this.content = options.content || '';
    this.size = options.size || 'md'; // sm, md, lg, xl
    this.closeOnBackdrop = options.closeOnBackdrop !== false;
    this.closeOnEscape = options.closeOnEscape !== false;
    this.backdrop = null;
    this.modal = null;
    this.onClose = options.onClose || null;
  }

  /**
   * Create modal HTML
   * @returns {HTMLElement}
   */
  createModal() {
    const backdrop = document.createElement('div');
    backdrop.className = 'fixed inset-0 bg-black/50 z-[1040] animate-fade-in';
    
    const container = document.createElement('div');
    container.className = 'fixed inset-0 flex items-center justify-center z-[1050] p-4 overflow-y-auto';
    
    const sizeClasses = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-2xl',
      xl: 'max-w-4xl',
    };
    
    const modal = document.createElement('div');
    modal.className = `bg-white rounded-lg shadow-2xl ${sizeClasses[this.size]} w-full animate-slide-down`;
    modal.innerHTML = `
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-xl font-bold text-gray-900">${DOM.escapeHtml(this.title)}</h3>
        <button class="modal-close p-1 hover:bg-gray-100 rounded transition-colors" 
                aria-label="Close modal">
          <svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
      <div class="modal-body p-6">
        ${this.content}
      </div>
    `;
    
    container.appendChild(modal);
    
    this.backdrop = backdrop;
    this.modal = container;
    
    return { backdrop, container };
  }

  /**
   * Show modal
   */
  show() {
    const { backdrop, container } = this.createModal();
    
    // Close button
    const closeBtn = container.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => this.close());
    
    // Close on backdrop click
    if (this.closeOnBackdrop) {
      backdrop.addEventListener('click', () => this.close());
    }
    
    // Close on Escape key
    if (this.closeOnEscape) {
      this.escapeHandler = (e) => {
        if (e.key === 'Escape') {
          this.close();
        }
      };
      document.addEventListener('keydown', this.escapeHandler);
    }
    
    // Add to DOM
    document.body.appendChild(backdrop);
    document.body.appendChild(container);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    return this;
  }

  /**
   * Close modal
   */
  close() {
    if (this.backdrop) {
      this.backdrop.style.animation = 'fadeOut 0.2s ease-out';
    }
    
    if (this.modal) {
      this.modal.style.animation = 'fadeOut 0.2s ease-out';
    }
    
    setTimeout(() => {
      if (this.backdrop) this.backdrop.remove();
      if (this.modal) this.modal.remove();
      
      // Remove escape handler
      if (this.escapeHandler) {
        document.removeEventListener('keydown', this.escapeHandler);
      }
      
      // Restore body scroll
      document.body.style.overflow = '';
      
      // Call onClose callback
      if (this.onClose) {
        this.onClose();
      }
    }, 200);
  }

  /**
   * Update modal content
   * @param {string} content - New content HTML
   */
  updateContent(content) {
    if (this.modal) {
      const body = this.modal.querySelector('.modal-body');
      if (body) {
        body.innerHTML = content;
      }
    }
  }

  /**
   * Update modal title
   * @param {string} title - New title
   */
  updateTitle(title) {
    if (this.modal) {
      const titleEl = this.modal.querySelector('h3');
      if (titleEl) {
        titleEl.textContent = title;
      }
    }
  }
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Object} options - Modal options
 * @returns {Promise<boolean>}
 */
export async function confirm(message, options = {}) {
  return new Promise((resolve) => {
    const content = `
      <p class="text-gray-700 mb-6">${DOM.escapeHtml(message)}</p>
      <div class="flex gap-3 justify-end">
        <button class="btn btn-secondary modal-cancel">
          ${options.cancelText || 'Cancel'}
        </button>
        <button class="btn btn-primary modal-confirm">
          ${options.confirmText || 'Confirm'}
        </button>
      </div>
    `;
    
    const modal = new Modal({
      title: options.title || 'Confirm',
      content: content,
      size: 'sm',
      closeOnBackdrop: false,
      onClose: () => resolve(false),
    });
    
    modal.show();
    
    // Wait for DOM to be ready
    setTimeout(() => {
      const cancelBtn = modal.modal.querySelector('.modal-cancel');
      const confirmBtn = modal.modal.querySelector('.modal-confirm');
      
      if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
          modal.close();
          resolve(false);
        });
      }
      
      if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
          modal.close();
          resolve(true);
        });
      }
    }, 0);
  });
}

/**
 * Show alert dialog
 * @param {string} message - Alert message
 * @param {Object} options - Modal options
 * @returns {Promise<void>}
 */
export async function alert(message, options = {}) {
  return new Promise((resolve) => {
    const content = `
      <p class="text-gray-700 mb-6">${DOM.escapeHtml(message)}</p>
      <div class="flex justify-end">
        <button class="btn btn-primary modal-ok">
          ${options.okText || 'OK'}
        </button>
      </div>
    `;
    
    const modal = new Modal({
      title: options.title || 'Alert',
      content: content,
      size: 'sm',
      onClose: () => resolve(),
    });
    
    modal.show();
    
    setTimeout(() => {
      const okBtn = modal.modal.querySelector('.modal-ok');
      if (okBtn) {
        okBtn.addEventListener('click', () => {
          modal.close();
          resolve();
        });
      }
    }, 0);
  });
}

export default Modal;
