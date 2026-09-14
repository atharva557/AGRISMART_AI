# AgriSmart AI - Build System

## Overview

This project now uses a modern build system with Webpack and Tailwind CSS to optimize frontend assets.

## Prerequisites

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **npm** (comes with Node.js)
   - Verify installation: `npm --version`

## Installation

```powershell
# Install dependencies
npm install
```

This will install:
- Webpack (module bundler)
- Tailwind CSS (utility-first CSS)
- PostCSS & Autoprefixer (CSS processing)
- Terser (JavaScript minification)
- Other build tools

## Development

### Start Development Build (with watch mode)

```powershell
# Build CSS and watch for changes
npm run build:css:dev

# In another terminal, build JavaScript and watch
npm run dev
```

This will:
- Compile Tailwind CSS with all utilities
- Bundle JavaScript modules
- Watch for file changes and rebuild automatically
- Generate source maps for debugging

### Build for Production

```powershell
# Build everything for production
npm run build:all
```

This will:
- Purge unused Tailwind CSS classes
- Minify CSS and JavaScript
- Remove console.log statements
- Optimize bundle size
- Generate source maps

## Project Structure

```
app/static/
├── css/
│   ├── src/
│   │   └── main.css         # Tailwind source (edit this)
│   └── dist/
│       └── main.min.css     # Compiled CSS (generated)
│
├── js/
│   ├── src/
│   │   ├── core/            # Core modules (API, config)
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-specific logic
│   │   ├── utils/           # Utility functions
│   │   └── main.js          # Main entry point
│   └── dist/
│       ├── main.min.js      # Core bundle (generated)
│       ├── home.min.js      # Home page bundle (generated)
│       ├── disease.min.js   # Disease page bundle (generated)
│       └── advisory.min.js  # Advisory page bundle (generated)
│
└── images/                  # Static images
```

## Scripts

| Script | Command | Description |
|--------|---------|-------------|
| Development CSS | `npm run build:css:dev` | Build CSS with watch mode |
| Development JS | `npm run dev` | Build JS with watch mode |
| Production CSS | `npm run build:css` | Build and minify CSS |
| Production JS | `npm run build` | Build and minify JS |
| Production All | `npm run build:all` | Build everything for production |
| Clean | `npm run clean` | Remove generated files |

## How It Works

### CSS Processing

1. **Source**: `app/static/css/src/main.css`
   - Imports Tailwind directives
   - Contains custom component styles
   - Uses @layer for organization

2. **Processing**:
   - Tailwind scans HTML and JS files for class usage
   - PostCSS processes the CSS
   - Autoprefixer adds vendor prefixes
   - PurgeCSS removes unused classes (production only)
   - CSS is minified

3. **Output**: `app/static/css/dist/main.min.css`
   - Single optimized CSS file
   - Typically < 50KB (vs 3MB+ unoptimized Tailwind)

### JavaScript Bundling

1. **Source**: Multiple files in `app/static/js/src/`
   - Modular ES6 modules
   - Separated by concern (core, components, utils)
   - Page-specific bundles

2. **Processing**:
   - Webpack resolves import/export statements
   - Bundles related modules together
   - Code splitting creates separate bundles
   - Terser minifies the output
   - Source maps for debugging

3. **Output**: `app/static/js/dist/`
   - `main.min.js` - Loaded on all pages (~15KB)
   - `home.min.js` - Home page only (~5KB)
   - `disease.min.js` - Disease detection (~10KB)
   - `advisory.min.js` - Advisory dashboard (~8KB)

## Updating Templates

After building, update your HTML templates to use the compiled assets:

### Before (Development - CDN):
```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="/static/js/app.js"></script>
<script src="/static/js/ui.js"></script>
```

### After (Production - Bundled):
```html
<link rel="stylesheet" href="/static/css/dist/main.min.css">
<script src="/static/js/dist/main.min.js"></script>
<script src="/static/js/dist/home.min.js"></script> <!-- Page-specific -->
```

## Configuration

### Tailwind CSS (`tailwind.config.js`)

Customize:
- Color palette
- Fonts
- Spacing
- Breakpoints
- Plugins

```javascript
module.exports = {
  content: ['./app/templates/**/*.html', './app/static/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        // Your custom colors
      }
    }
  }
}
```

### Webpack (`webpack.config.js`)

Customize:
- Entry points
- Output paths
- Loaders
- Plugins
- Optimization

## Troubleshooting

### "npm: command not found"
- Install Node.js from https://nodejs.org/

### Build errors
```powershell
# Clear node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

### CSS not updating
```powershell
# Clear dist folder and rebuild
npm run clean
npm run build:all
```

### JavaScript errors
- Check browser console for errors
- Verify source maps are generated
- Check import/export syntax in modules

## Performance Benefits

### Before Build System:
- **CSS**: 3+ MB (full Tailwind CDN)
- **JS**: Multiple HTTP requests (7 files)
- **Total Load**: 3+ MB, 11+ requests

### After Build System:
- **CSS**: ~40KB (purged Tailwind)
- **JS**: ~40KB total (4 bundles with code splitting)
- **Total Load**: ~80KB, 5 requests

**Result**: ~97% reduction in CSS, 60% reduction in HTTP requests

## Next Steps

1. Replace CDN links with built assets in templates
2. Test all pages work correctly
3. Deploy with production builds
4. Set up CI/CD to auto-build on deployment

## Support

- **Webpack Docs**: https://webpack.js.org/
- **Tailwind Docs**: https://tailwindcss.com/docs
- **PostCSS Docs**: https://postcss.org/

---

**Built with ❤️ for AgriSmart AI**
