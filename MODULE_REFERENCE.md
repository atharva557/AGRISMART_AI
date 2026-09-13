# AgriSmart AI - JavaScript Module Reference

## Overview

This document provides a complete reference for all JavaScript modules in the AgriSmart AI application.

---

## Core Modules

### API Service (`core/api.js`)

Centralized API communication layer.

**Usage:**
```javascript
import API from './core/api.js';

// Check health
const isHealthy = await API.checkHealth();

// Disease prediction
const result = await API.predictDisease(imageFile, (progress) => {
  console.log(`Progress: ${progress}%`);
});

// Crop recommendation
const crops = await API.recommendCrops(payload);

// Create request envelope
const envelope = API.createEnvelope('A', 'dataset_benchmark', inputs);

// Create measurement
const measurement = API.createMeasurement(42.5, 'kg', 'observed');
```

**Methods:**
- `get(endpoint, options)` - GET request
- `post(endpoint, data, options)` - POST request
- `uploadFile(endpoint, formData, onProgress)` - File upload with progress
- `predictDisease(file, onProgress)` - Disease detection API
- `recommendCrops(data)` - Module A
- `adviseIrrigation(data)` - Module B
- `adviseWeather(data)` - Module C
- `scoreSustainability(data)` - Module D
- `createEnvelope(module, purpose, inputs, farm, cropContext)` - Create request
- `createMeasurement(value, unit, kind)` - Create measurement object
- `isSuccess(response)` - Check if response is successful
- `getErrorMessage(response)` - Extract error message

---

## Component Modules

### UI Components (`components/ui.js`)

Reusable UI state management and feedback.

**Usage:**
```javascript
import UI from './components/ui.js';

// Loading states
UI.showLoading(container, 'Processing...');
UI.hideLoading(container);

// Alerts
UI.showSuccess(container, 'Operation completed!');
UI.showError(container, 'Something went wrong');
UI.showWarning(container, 'Please review your input');
UI.showInfo(container, 'FYI: System will restart soon');

// Toast notifications
UI.toast('File uploaded successfully', 'success', 3000);

// Modals
const confirmed = await UI.confirm('Delete this item?', 'Confirm Delete');
if (confirmed) {
  // Delete item
}

// Element visibility
UI.show(element);
UI.hide(element);
UI.toggle(element);

// Element state
UI.disable(button);
UI.enable(button);

// Navigation
UI.setActiveNav('/disease');
UI.scrollToTop();
```

**Methods:**
- `showLoading(container, message)` - Show loading overlay
- `hideLoading(container)` - Hide loading overlay
- `showAlert(container, message, type, title)` - Generic alert
- `showSuccess/Error/Warning/Info(container, message, title)` - Specific alerts
- `toast(message, type, duration)` - Toast notification
- `confirm(message, title)` - Confirmation dialog (returns Promise<boolean>)
- `show/hide/toggle(element)` - Element visibility
- `disable/enable(element)` - Element state
- `setActiveNav(path)` - Set active nav item
- `scrollToTop()` - Smooth scroll to top

### Form Handler (`components/form.js`)

Reusable form handling and validation.

**Usage:**
```javascript
import { createFormHandler } from './components/form.js';

// Create form handler
const form = createFormHandler('#myForm');

// Get form data
const data = form.getData();
const numericValue = form.getNumber('age');

// Set form values
form.setData({ name: 'John', age: 30 });

// Validate and submit
form.onSubmit(async (data) => {
  const response = await API.post('/api/submit', data);
  return { 
    success: response.status === 'OK',
    message: response.message 
  };
}, outputContainer);

// Manual control
form.disable();
form.enable();
form.reset();
const isValid = form.validate();
```

**Methods:**
- `getData()` - Get all form data as object
- `getNumber(name)` - Get numeric value
- `setData(data)` - Populate form with data
- `validate()` - Validate form (HTML5)
- `reset()` - Reset form
- `disable/enable()` - Disable/enable all fields
- `onSubmit(handler, outputContainer)` - Handle form submission

### Modal (`components/modal.js`)

Customizable modal dialogs.

**Usage:**
```javascript
import { Modal, confirm, alert } from './components/modal.js';

// Create custom modal
const modal = new Modal({
  title: 'User Profile',
  content: '<div>Profile content here</div>',
  size: 'lg', // sm, md, lg, xl
  closeOnBackdrop: true,
  closeOnEscape: true,
  onClose: () => console.log('Modal closed'),
});

modal.show();

// Update modal
modal.updateTitle('Edit Profile');
modal.updateContent('<div>New content</div>');
modal.close();

// Confirmation dialog
const confirmed = await confirm('Delete this file?', {
  title: 'Confirm Deletion',
  confirmText: 'Delete',
  cancelText: 'Cancel',
});

// Alert dialog
await alert('File has been deleted successfully', {
  title: 'Success',
  okText: 'Got it',
});
```

### Notification System (`components/notification.js`)

Toast-style notifications with auto-dismiss.

**Usage:**
```javascript
import Notification from './components/notification.js';

// Show notifications
Notification.success('File uploaded successfully');
Notification.error('Failed to connect to server');
Notification.warning('Unsaved changes will be lost');
Notification.info('New version available');

// Custom duration (0 = permanent)
const notif = Notification.show('Processing...', 'info', 0);

// Close specific notification
notif.close();

// Clear all notifications
Notification.clearAll();

// Custom notification
Notification.show('Custom message', 'success', 5000);
```

---

## Utility Modules

### DOM Utilities (`utils/dom.js`)

DOM manipulation helpers.

**Usage:**
```javascript
import { DOM } from './utils/dom.js';

// Element selection
const element = DOM.byId('myId');
const first = DOM.qs('.myClass');
const all = DOM.qsa('.myClass');

// Event listeners
DOM.addEventListeners(buttons, 'click', handleClick);

// Security
const safe = DOM.escapeHtml(userInput);

// Scrolling
DOM.scrollTo('#section', 100); // offset 100px
const isVisible = DOM.isInViewport(element);

// Device detection
if (DOM.isMobile()) {
  // Mobile-specific code
}
```

### Format Utilities (`utils/format.js`)

Data formatting for display.

**Usage:**
```javascript
import { Format } from './utils/format.js';

// Dates
Format.date(new Date(), 'short'); // "Jan 15, 2026"
Format.date(new Date(), 'long');  // "January 15, 2026, 10:30 AM"
Format.date(new Date(), 'time');  // "10:30:45 AM"

// Numbers
Format.number(1234.5678, 2);  // "1234.57"
Format.fileSize(1024000);      // "1000 KB"

// Strings
Format.capitalize('hello');    // "Hello"
Format.truncate('Long text...', 10, '...'); // "Long text..."
```

### Helper Utilities (`utils/helpers.js`)

General purpose helpers.

**Usage:**
```javascript
import { Helpers } from './utils/helpers.js';

// Performance
const debouncedSearch = Helpers.debounce(search, 300);
const throttledScroll = Helpers.throttle(handleScroll, 100);

// IDs
const id = Helpers.uniqueId('user'); // "user-1641234567890-abc123"

// Clipboard
await Helpers.copyToClipboard('Text to copy');

// Query strings
const params = Helpers.parseQueryString('?foo=bar&baz=qux');
// {foo: 'bar', baz: 'qux'}

// Delay
await Helpers.wait(1000); // Wait 1 second

// Storage
Helpers.storage.set('user', { name: 'John' });
const user = Helpers.storage.get('user');
Helpers.storage.remove('user');
Helpers.storage.clear();
```

### Validation Utilities (`utils/validation.js`)

Input validation and sanitization.

**Usage:**
```javascript
import { Validation } from './utils/validation.js';

// Basic validation
Validation.isEmail('user@example.com');
Validation.isPhone('+1234567890');
Validation.isURL('https://example.com');
Validation.isNumeric('42.5');
Validation.isInteger('42');
Validation.isPositive(10);
Validation.isRequired(value);
Validation.isInRange(5, 0, 10);
Validation.isLengthValid('hello', 3, 10);

// File validation
const result = Validation.validateImageFile(file, 10); // 10MB max
if (!result.valid) {
  console.error(result.error);
}

Validation.isFileType(file, ['image/jpeg', 'image/png']);
Validation.isFileSize(file, 5 * 1024 * 1024); // 5MB

// Sanitization
const safe = Validation.sanitizeString(userInput);
const num = Validation.sanitizeNumber('42.567', 2); // 42.57

// Form validation
const result = Validation.validateForm(form, {
  email: { 
    required: true, 
    email: true 
  },
  age: { 
    required: true, 
    numeric: true, 
    min: 18, 
    max: 100 
  },
  password: { 
    required: true, 
    minLength: 8,
    custom: (value) => {
      if (!/[A-Z]/.test(value)) {
        return 'Password must contain uppercase letter';
      }
    }
  },
});

if (!result.valid) {
  Validation.showErrors(form, result.errors);
} else {
  Validation.clearErrors(form);
}
```

---

## Page Modules

### Home Page (`pages/home.js`)

Landing page functionality.

**Initialization:**
- Automatically loads on page load
- Sets up hero animations

### Disease Detection (`pages/disease.js`)

Disease detection page with file upload.

**Features:**
- File upload with drag & drop
- Image preview
- File validation (type, size)
- Analysis with progress tracking
- Result display

**Exports:**
- `handleAnalyze()` - Trigger analysis
- `handleClear()` - Clear form and results

### Advisory Dashboard (`pages/advisory.js`)

Advisory modules A-D integration.

**Features:**
- Module A: Crop recommendation
- Module B: Irrigation advisory
- Module C: Weather advisory
- Module D: Sustainability scoring

**Exports:**
- `initModuleA()` - Initialize crop module
- `initModuleB()` - Initialize irrigation module
- `initModuleC()` - Initialize weather module
- `initModuleD()` - Initialize sustainability module

---

## Global Access

All modules are available globally for compatibility:

```javascript
// Available on window object
window.API
window.UI
window.DOM
window.Format
window.Helpers
window.Validation
window.FormHandler
window.createFormHandler
window.Modal
window.modalConfirm
window.modalAlert
window.Notification
```

---

## Module Import Examples

### ES6 Modules
```javascript
import API from './core/api.js';
import UI from './components/ui.js';
import { Format } from './utils/format.js';
```

### Global Access (Legacy)
```html
<script src="/static/js/dist/main.min.js"></script>
<script>
  // Access via window
  API.checkHealth();
  UI.toast('Hello');
  Notification.success('Done!');
</script>
```

---

## Best Practices

1. **Always validate user input:**
   ```javascript
   const result = Validation.validateImageFile(file);
   if (!result.valid) {
     UI.toast(result.error, 'error');
     return;
   }
   ```

2. **Use loading states:**
   ```javascript
   UI.showLoading(container, 'Processing...');
   try {
     const result = await API.post('/api/endpoint', data);
     UI.hideLoading(container);
     UI.showSuccess(container, 'Success!');
   } catch (error) {
     UI.hideLoading(container);
     UI.showError(container, 'Failed');
   }
   ```

3. **Sanitize user input:**
   ```javascript
   const safe = DOM.escapeHtml(userInput);
   element.innerHTML = safe;
   ```

4. **Use form handlers:**
   ```javascript
   const form = createFormHandler('#myForm');
   form.onSubmit(async (data) => {
     return await API.post('/api/submit', data);
   }, outputContainer);
   ```

5. **Provide user feedback:**
   ```javascript
   Notification.success('Changes saved');
   Notification.error('Failed to save');
   ```

---

## Testing

Test modules in browser console:

```javascript
// Test API
await API.checkHealth();

// Test UI
UI.toast('Test notification', 'success');

// Test validation
Validation.isEmail('test@example.com');

// Test modal
await modalConfirm('Test confirm?');
```

---

## Support

- **Module Issues:** Check browser console for errors
- **API Issues:** Check network tab in DevTools
- **Build Issues:** See `BUILD_README.md`

---

**Version:** 1.0.1  
**Last Updated:** September 13, 2026
