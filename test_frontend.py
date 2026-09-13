"""
Frontend Integration Test
Verify all routes and pages are working correctly
"""

import sys
from app import create_app

def test_routes():
    """Test that all routes return 200 status"""
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
    
    print("\n" + "="*60)
    print("FRONTEND INTEGRATION TEST")
    print("="*60 + "\n")
    
    all_passed = True
    
    for method, path, name in routes:
        response = client.get(path) if method == 'GET' else client.post(path)
        status = response.status_code
        passed = status == 200
        
        symbol = "✓" if passed else "✗"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {name:30} {method:6} {path:30} [{status}]")
        
        if not passed:
            all_passed = False
    
    # Test error pages
    print("\nError Pages:")
    error_routes = [
        ('/nonexistent', 404, '404 Not Found'),
    ]
    
    for path, expected_status, name in error_routes:
        response = client.get(path)
        status = response.status_code
        passed = status == expected_status
        
        symbol = "✓" if passed else "✗"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {name:30} GET    {path:30} [{status}]")
        
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("\033[92m✓ ALL TESTS PASSED\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m✗ SOME TESTS FAILED\033[0m")
        print("="*60 + "\n")
        return 1

def test_static_files():
    """Test that all static files exist"""
    import os
    from pathlib import Path
    
    print("\n" + "="*60)
    print("STATIC FILES CHECK")
    print("="*60 + "\n")
    
    base_path = Path(__file__).parent / 'app' / 'static'
    
    files = [
        'css/base.css',
        'css/components.css',
        'css/pages.css',
        'js/utils.js',
        'js/api.js',
        'js/ui.js',
        'js/validation.js',
        'js/upload.js',
        'js/disease.js',
        'js/app.js',
    ]
    
    all_exist = True
    
    for file_path in files:
        full_path = base_path / file_path
        exists = full_path.exists()
        
        symbol = "✓" if exists else "✗"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {file_path}")
        
        if not exists:
            all_exist = False
    
    print("\n" + "="*60)
    if all_exist:
        print("\033[92m✓ ALL STATIC FILES FOUND\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m✗ SOME STATIC FILES MISSING\033[0m")
        print("="*60 + "\n")
        return 1

def test_templates():
    """Test that all templates exist"""
    from pathlib import Path
    
    print("\n" + "="*60)
    print("TEMPLATES CHECK")
    print("="*60 + "\n")
    
    base_path = Path(__file__).parent / 'app' / 'templates'
    
    templates = [
        'base.html',
        'home.html',
        'disease_upload.html',
        'disease_result.html',
        'advisory.html',
        'about.html',
        'error.html',
        'components/header.html',
        'components/footer.html',
    ]
    
    all_exist = True
    
    for template in templates:
        full_path = base_path / template
        exists = full_path.exists()
        
        symbol = "✓" if exists else "✗"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {template}")
        
        if not exists:
            all_exist = False
    
    print("\n" + "="*60)
    if all_exist:
        print("\033[92m✓ ALL TEMPLATES FOUND\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m✗ SOME TEMPLATES MISSING\033[0m")
        print("="*60 + "\n")
        return 1

if __name__ == '__main__':
    exit_code = 0
    
    # Run all tests
    exit_code |= test_templates()
    exit_code |= test_static_files()
    exit_code |= test_routes()
    
    if exit_code == 0:
        print("\n\033[92m" + "="*60)
        print("🎉 FRONTEND INTEGRATION COMPLETE - ALL CHECKS PASSED")
        print("="*60 + "\033[0m\n")
        print("You can now run the application:")
        print("  python run.py")
        print("\nThen visit: http://127.0.0.1:5000\n")
    else:
        print("\n\033[91m" + "="*60)
        print("⚠️  SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("="*60 + "\033[0m\n")
    
    sys.exit(exit_code)
