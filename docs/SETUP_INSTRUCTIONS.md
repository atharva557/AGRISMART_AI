# AgriSmart AI - Setup Instructions

## Quick Start Guide

Follow these steps to set up the build system and run the application.

### Step 1: Install Node.js

1. Download Node.js from: https://nodejs.org/
2. Choose the LTS (Long Term Support) version
3. Run the installer
4. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

### Step 2: Install Dependencies

Open PowerShell in the project root and run:

```powershell
cd d:\PARV\Projects\AGRISMART_AI
npm install
```

This will install all required packages (may take 2-3 minutes).

### Step 3: Build Assets

#### Option A: Development Build (with auto-rebuild)

**Terminal 1 - CSS:**
```powershell
npm run build:css:dev
```

**Terminal 2 - JavaScript:**
```powershell
npm run dev
```

Keep both terminals open. Files will rebuild automatically when you make changes.

#### Option B: Production Build (one-time)

```powershell
npm run build:all
```

This creates optimized, minified assets for production.

### Step 4: Update HTML Templates

The templates need to be updated to use the compiled assets instead of CDN links.

**Files to update:**
- `app/templates/base.html`
- `app/templates/home.html`
- `app/templates/advisory.html`
- `app/templates/disease_upload.html`

**Change FROM:**
```html
<!-- Old CDN approach -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="/static/js/app.js"></script>
<script src="/static/js/ui.js"></script>
```

**Change TO:**
```html
<!-- New bundled approach -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/dist/main.min.css') }}">
<script src="{{ url_for('static', filename='js/dist/main.min.js') }}"></script>
<!-- Page-specific bundle -->
<script src="{{ url_for('static', filename='js/dist/home.min.js') }}"></script>
```

### Step 5: Run the Application

```powershell
python run.py
```

Visit: http://127.0.0.1:5000

### Step 6: Verify Everything Works

1. ✅ Home page loads with hero image
2. ✅ CSS is properly styled (not raw HTML)
3. ✅ Navigation works
4. ✅ Forms submit correctly
5. ✅ Console shows no errors (F12)

---

## File Structure After Setup

```
AGRISMART_AI/
├── node_modules/          # Installed packages (gitignored)
├── package.json           # Dependencies and scripts
├── webpack.config.js      # Webpack configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
│
├── app/static/
│   ├── css/
│   │   ├── src/
│   │   │   └── main.css               # Source CSS (EDIT THIS)
│   │   └── dist/
│   │       └── main.min.css           # Compiled CSS (GENERATED)
│   │
│   └── js/
│       ├── src/
│       │   ├── main.js                # Main entry (EDIT THIS)
│       │   ├── core/
│       │   │   └── api.js             # API service
│       │   ├── components/
│       │   │   └── ui.js              # UI components
│       │   ├── utils/
│       │   │   ├── dom.js             # DOM utilities
│       │   │   ├── format.js          # Formatting
│       │   │   └── helpers.js         # Helpers
│       │   └── pages/
│       │       ├── home.js            # Home page logic
│       │       ├── disease.js         # Disease detection
│       │       └── advisory.js        # Advisory dashboard
│       │
│       └── dist/
│           ├── main.min.js            # Core bundle (GENERATED)
│           ├── home.min.js            # Home page bundle (GENERATED)
│           ├── disease.min.js         # Disease page bundle (GENERATED)
│           └── advisory.min.js        # Advisory page bundle (GENERATED)
```

---

## Development Workflow

### Making CSS Changes

1. Edit: `app/static/css/src/main.css`
2. Save the file
3. Build process automatically rebuilds
4. Refresh browser (Ctrl + Shift + R)

### Making JavaScript Changes

1. Edit files in: `app/static/js/src/`
2. Save the file
3. Build process automatically rebuilds
4. Refresh browser (Ctrl + Shift + R)

### Adding New Pages

1. Create new file: `app/static/js/src/pages/mypage.js`
2. Update `webpack.config.js` entry points:
   ```javascript
   entry: {
     main: './app/static/js/src/main.js',
     mypage: './app/static/js/src/pages/mypage.js',  // Add this
   }
   ```
3. Rebuild: `npm run build`
4. Add to template:
   ```html
   <script src="{{ url_for('static', filename='js/dist/mypage.min.js') }}"></script>
   ```

---

## Troubleshooting

### "npm: command not found"
**Problem:** Node.js not installed  
**Solution:** Install Node.js from https://nodejs.org/

### "Cannot find module..."
**Problem:** Dependencies not installed  
**Solution:** 
```powershell
Remove-Item -Recurse -Force node_modules
npm install
```

### CSS/JS not updating
**Problem:** Browser cache or build not running  
**Solution:**
1. Check terminal for build errors
2. Clear browser cache (Ctrl + Shift + Delete)
3. Hard refresh (Ctrl + Shift + R)
4. Restart build process

### Build errors
**Problem:** Syntax error in source files  
**Solution:**
1. Check terminal for error message
2. Fix syntax error in indicated file
3. Save file to trigger rebuild

### Assets not loading (404)
**Problem:** Template references wrong path  
**Solution:** Verify paths match:
```html
<!-- Correct -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/dist/main.min.css') }}">

<!-- Wrong -->
<link rel="stylesheet" href="/static/css/main.css">
```

---

## Production Deployment

### Before Deploying:

1. **Build production assets:**
   ```powershell
   npm run build:all
   ```

2. **Test production build locally:**
   ```powershell
   python run.py
   ```

3. **Verify:**
   - All pages load correctly
   - CSS is minified (view source)
   - No console errors
   - Lighthouse score > 90

4. **Commit changes:**
   ```powershell
   git add .
   git commit -m "Add build system and optimized assets"
   ```

### What to Deploy:

**Include:**
- `app/static/css/dist/` (compiled CSS)
- `app/static/js/dist/` (compiled JS)
- `package.json` (for CI/CD)
- `webpack.config.js`
- `tailwind.config.js`
- All Python files and templates

**Exclude (already in .gitignore):**
- `node_modules/`
- Source files are optional (keep for editing)

---

## Performance Benefits

### Before:
- 🔴 Tailwind CDN: 3+ MB
- 🔴 Multiple JS files: 7 requests
- 🔴 Total: ~3.5 MB, 11+ requests

### After:
- 🟢 Compiled CSS: ~40 KB
- 🟢 Bundled JS: ~40 KB total
- 🟢 Total: ~80 KB, 5 requests

**Result:** 97% size reduction, 55% fewer requests!

---

## Next Steps

1. ✅ Build system set up
2. ✅ Assets compiled
3. ⏳ Update templates to use compiled assets
4. ⏳ Test all pages
5. ⏳ Remove old CSS/JS files
6. ⏳ Deploy to production

---

## Support

**Build System Issues:**
- Check: `BUILD_README.md` for detailed build documentation
- Webpack docs: https://webpack.js.org/
- Tailwind docs: https://tailwindcss.com/

**Application Issues:**
- Check: `DEPLOYMENT.md` for deployment guide
- Check: `FRONTEND_README.md` for frontend documentation

---

**Setup completed? Run the verification:**
```powershell
python verify_photo_changes.py
```

This will verify all files are in place and the build system is working correctly.
