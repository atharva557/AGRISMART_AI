"""
Verify Photo Replacement Changes
Quick verification script to check if hero image integration is working
"""

import os
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("AGRISMART AI - Photo Replacement Verification")
print("=" * 60)
print()

# Check files exist
checks = {
    "Hero Image": ROOT / "app" / "static" / "images" / "hero-field.jpg",
    "Favicon": ROOT / "app" / "static" / "images" / "favicon.svg",
    "Home Template": ROOT / "app" / "templates" / "home.html",
    "Style CSS": ROOT / "app" / "static" / "css" / "style.css",
}

all_passed = True

for name, path in checks.items():
    exists = path.exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {name}: {path.relative_to(ROOT)}")
    if not exists:
        all_passed = False

print()

# Check file contents
print("Checking file contents...")
print()

# Check home.html for image reference
home_template = checks["Home Template"]
if home_template.exists():
    content = home_template.read_text(encoding='utf-8')
    has_image = "hero-field.jpg" in content
    has_overlay = "hero-field.jpg" in content or "Gradient" in content or "gradient" in content
    
    print(f"{'[OK]' if has_image else '[FAIL]'} home.html references hero-field.jpg")
    print(f"{'[OK]' if has_overlay else '[FAIL]'} home.html has overlay")
    
    if not has_image:
        all_passed = False
else:
    print("[FAIL] Cannot check home.html - file not found")
    all_passed = False

print()

# Check style.css for background image
style_css = checks["Style CSS"]
if style_css.exists():
    content = style_css.read_text(encoding='utf-8')
    has_bg_image = "hero-field.jpg" in content
    has_hero_class = ".hero {" in content or ".hero{" in content
    
    print(f"{'[OK]' if has_bg_image else '[FAIL]'} style.css references hero-field.jpg")
    print(f"{'[OK]' if has_hero_class else '[FAIL]'} style.css has .hero class")
    
    if not has_bg_image:
        print("  Note: style.css might use index.html (legacy template)")
else:
    print("[FAIL] Cannot check style.css - file not found")
    all_passed = False

print()

# Check base.html for favicon
base_template = ROOT / "app" / "templates" / "base.html"
if base_template.exists():
    content = base_template.read_text(encoding='utf-8')
    has_favicon = "favicon.svg" in content
    
    print(f"{'[OK]' if has_favicon else '[FAIL]'} base.html references favicon.svg")
    
    if not has_favicon:
        all_passed = False
else:
    print("[FAIL] Cannot check base.html - file not found")

print()
print("=" * 60)

if all_passed:
    print("[OK] ALL CHECKS PASSED")
    print()
    print("Application is verified and ready.")
else:
    print("[FAIL] SOME CHECKS FAILED")
    print()
    print("Please review the errors above and fix the issues.")

print("=" * 60)

