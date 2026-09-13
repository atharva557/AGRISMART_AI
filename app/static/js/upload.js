/**
 * AgriSmart AI - File Upload Handler
 * Image upload, validation, and preview functionality
 */

const FileUpload = {
  // Configuration
  config: {
    maxFileSize: 10 * 1024 * 1024, // 10MB (matches Flask config)
    allowedTypes: ['image/jpeg', 'image/jpg', 'image/png'],
    allowedExtensions: ['jpg', 'jpeg', 'png']
  },

  /**
   * Validate file
   * @param {File} file - File to validate
   * @returns {Object} - { valid: boolean, error: string }
   */
  validateFile(file) {
    if (!file) {
      return { valid: false, error: 'No file selected' };
    }

    // Check file type
    if (!this.config.allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `Invalid file type. Allowed: ${this.config.allowedExtensions.join(', ').toUpperCase()}`
      };
    }

    // Check file size
    if (file.size > this.config.maxFileSize) {
      return {
        valid: false,
        error: `File too large. Maximum size: ${Utils.formatFileSize(this.config.maxFileSize)}`
      };
    }

    // Check file extension
    const extension = file.name.split('.').pop().toLowerCase();
    if (!this.config.allowedExtensions.includes(extension)) {
      return {
        valid: false,
        error: `Invalid file extension. Allowed: ${this.config.allowedExtensions.join(', ').toUpperCase()}`
      };
    }

    return { valid: true, error: null };
  },

  /**
   * Create image preview
   * @param {File} file - Image file
   * @param {HTMLElement} container - Preview container
   * @returns {Promise<void>}
   */
  async createPreview(file, container) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        container.innerHTML = `
          <div class="relative">
            <img src="${e.target.result}" 
                 alt="Preview" 
                 class="max-w-full max-h-96 rounded-lg shadow-lg mx-auto">
            <div class="mt-4 text-center">
              <p class="text-sm text-gray-600">
                <span class="font-medium">${Utils.escapeHtml(file.name)}</span>
                <span class="text-gray-400 mx-2">·</span>
                <span>${Utils.formatFileSize(file.size)}</span>
              </p>
            </div>
          </div>
        `;
        resolve();
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  },

  /**
   * Clear preview
   * @param {HTMLElement} container - Preview container
   */
  clearPreview(container) {
    if (container) {
      container.innerHTML = '';
    }
  },

  /**
   * Compress image (optional, for reducing upload size)
   * @param {File} file - Image file
   * @param {number} maxWidth - Maximum width
   * @param {number} maxHeight - Maximum height
   * @param {number} quality - JPEG quality (0-1)
   * @returns {Promise<Blob>}
   */
  async compressImage(file, maxWidth = 1920, maxHeight = 1920, quality = 0.8) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        const img = new Image();

        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;

          // Calculate new dimensions
          if (width > height) {
            if (width > maxWidth) {
              height *= maxWidth / width;
              width = maxWidth;
            }
          } else {
            if (height > maxHeight) {
              width *= maxHeight / height;
              height = maxHeight;
            }
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob);
              } else {
                reject(new Error('Failed to compress image'));
              }
            },
            file.type,
            quality
          );
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = e.target.result;
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  },

  /**
   * Setup drag and drop
   * @param {HTMLElement} dropZone - Drop zone element
   * @param {Function} onDrop - Callback when file is dropped
   */
  setupDragAndDrop(dropZone, onDrop) {
    if (!dropZone) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('border-green-500', 'bg-green-50');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('border-green-500', 'bg-green-50');
      });
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        onDrop(files[0]);
      }
    });
  },

  /**
   * Setup file input
   * @param {HTMLElement} input - File input element
   * @param {Function} onChange - Callback when file is selected
   */
  setupFileInput(input, onChange) {
    if (!input) return;

    input.addEventListener('change', (e) => {
      const files = e.target.files;
      if (files.length > 0) {
        onChange(files[0]);
      }
    });
  },

  /**
   * Get file extension
   * @param {string} filename - File name
   * @returns {string}
   */
  getExtension(filename) {
    return filename.split('.').pop().toLowerCase();
  },

  /**
   * Get file type icon
   * @param {File} file - File object
   * @returns {string} - SVG icon HTML
   */
  getFileIcon(file) {
    const type = file.type;

    if (type.startsWith('image/')) {
      return `
        <svg class="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      `;
    }

    return `
      <svg class="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
      </svg>
    `;
  }
};

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FileUpload;
}
