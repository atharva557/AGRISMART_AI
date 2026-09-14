"""
Frontend Integration Test
Verify all routes, static assets, and templates are correct.

Changes from original:
- Added dead-template removal checks (result.html, index.html)
- Added _assistant_widget.html to active-templates list
- Health endpoint now returns model availability fields
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app

<<<<<<< HEAD

def test_routes():
    """Test that all active routes return 200 status."""
=======
def check_routes():
    """Test that all routes return 200 status"""
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
    app = create_app()
    client = app.test_client()

    routes = [
        ('GET', '/', 'Home Page'),
        ('GET', '/disease', 'Disease Upload'),
        ('GET', '/disease/result', 'Disease Result'),
        ('GET', '/advisory', 'Advisory Dashboard'),
        ('GET', '/about', 'About Page'),
        ('GET', '/api/health', 'Health Check'),
    ]

    print("\n" + "=" * 60)
    print("FRONTEND INTEGRATION TEST")
    print("=" * 60 + "\n")

    all_passed = True

    for method, path, name in routes:
        response = client.get(path) if method == 'GET' else client.post(path)
        status = response.status_code
        passed = status == 200

        symbol = "[OK]" if passed else "[FAIL]"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{symbol}{reset} {name:30} {method:6} {path:30} [{status}]")

        if not passed:
            all_passed = False

    # Test that non-existent routes return 404
    print("\nError Pages:")
    for path, expected_status, name in [('/nonexistent', 404, '404 Not Found')]:
        response = client.get(path)
        status = response.status_code
        passed = status == expected_status
        symbol = "[OK]" if passed else "[FAIL]"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{symbol}{reset} {name:30} GET    {path:30} [{status}]")
        if not passed:
            all_passed = False

    # Verify health endpoint returns model availability fields
    print("\nHealth endpoint fields:")
    resp = client.get('/api/health')
    data = resp.get_json() or {}
    has_models = 'models' in data
    symbol = "[OK]" if has_models else "[FAIL]"
    color = "\033[92m" if has_models else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} /api/health returns 'models' field: {has_models}")
    if not has_models:
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("\033[92m[OK] ALL ROUTES PASSED\033[0m")
        print("=" * 60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME ROUTES FAILED\033[0m")
        print("=" * 60 + "\n")
        return 1

<<<<<<< HEAD

def test_static_files():
    """Test that critical compiled static files exist."""
    print("\n" + "=" * 60)
=======
def check_static_files():
    """Test that critical static files exist"""
    import os
    from pathlib import Path
    
    print("\n" + "="*60)
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
    print("STATIC ASSETS CHECK")
    print("=" * 60 + "\n")

    base_path = ROOT / 'app' / 'static'

    files = [
        'css/dist/main.min.css',
        'js/dist/main.min.js',
        'js/dist/disease.min.js',
        'js/dist/advisory.min.js',
    ]

    all_exist = True
    for file in files:
        exists = (base_path / file).exists()
        symbol = "[OK]" if exists else "[FAIL]"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{symbol}{reset} {file}")
        if not exists:
            all_exist = False

    print("\n" + "=" * 60)
    if all_exist:
        print("\033[92m[OK] ALL STATIC ASSETS FOUND\033[0m")
        print("=" * 60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME STATIC ASSETS MISSING\033[0m")
        print("=" * 60 + "\n")
        return 1

<<<<<<< HEAD

def test_templates():
    """Test that active templates exist and confirmed-dead legacy templates have been removed."""
    print("\n" + "=" * 60)
=======
def check_templates():
    """Test that all required templates exist"""
    from pathlib import Path
    
    print("\n" + "="*60)
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
    print("TEMPLATES CHECK")
    print("=" * 60 + "\n")

    base_path = ROOT / 'app' / 'templates'

    # Active templates that MUST be present
    active_templates = [
        'base.html',
        'home.html',
        'disease_upload.html',
        'disease_result.html',
        'advisory.html',
        'about.html',
        'error.html',
        '_assistant_widget.html',
        'components/header.html',
        'components/footer.html',
    ]

    print("Active templates (must exist):")
    all_present = True
    for template in active_templates:
        exists = (base_path / template).exists()
        symbol = "[OK]" if exists else "[FAIL]"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{symbol}{reset} {template}")
        if not exists:
            all_present = False

    # Confirmed-dead legacy templates that MUST NOT be present
    dead_templates = [
        ('result.html',  'referenced non-existent url_for(main.index); never rendered by any route'),
        ('index.html',   'standalone legacy page; not integrated with the Flask application'),
    ]

    print("\nDead template removal check (must be absent):")
    all_absent = True
    for template, reason in dead_templates:
        present = (base_path / template).exists()
        absent = not present
        symbol = "[OK]" if absent else "[FAIL]"
        color = "\033[92m" if absent else "\033[91m"
        reset = "\033[0m"
        status_str = "correctly absent" if absent else f"STILL PRESENT — {reason}"
        print(f"{color}{symbol}{reset} {template}: {status_str}")
        if not absent:
            all_absent = False

    overall = all_present and all_absent
    print("\n" + "=" * 60)
    if overall:
        print("\033[92m[OK] ALL TEMPLATE CHECKS PASSED\033[0m")
        print("=" * 60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME TEMPLATE CHECKS FAILED\033[0m")
        print("=" * 60 + "\n")
        return 1

<<<<<<< HEAD

if __name__ == '__main__':
    exit_code = 0
    exit_code |= test_templates()
    exit_code |= test_static_files()
    exit_code |= test_routes()

=======
def test_routes():
    assert check_routes() == 0, 'One or more frontend routes failed'


def test_static_files():
    assert check_static_files() == 0, 'Required frontend assets are missing; run npm run build:all'


def test_templates():
    assert check_templates() == 0, 'Required frontend templates are missing'


if __name__ == '__main__':
    exit_code = 0
    
    # Run all tests
    exit_code |= check_templates()
    exit_code |= check_static_files()
    exit_code |= check_routes()
    
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
    if exit_code == 0:
        print("\n\033[92m" + "=" * 60)
        print("FRONTEND INTEGRATION COMPLETE - ALL CHECKS PASSED")
        print("=" * 60 + "\033[0m\n")
        print("Run the application with:  python run.py")
        print("Then visit:                http://127.0.0.1:5000\n")
    else:
        print("\n\033[91m" + "=" * 60)
        print("SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("=" * 60 + "\033[0m\n")

    sys.exit(exit_code)
