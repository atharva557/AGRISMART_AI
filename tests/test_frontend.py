"""
Frontend Integration Test
Verify all routes and pages are working correctly
"""

import sys
from html.parser import HTMLParser
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app

def check_routes():
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
        
        symbol = "[OK]" if passed else "[FAIL]"
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
        
        symbol = "[OK]" if passed else "[FAIL]"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {name:30} GET    {path:30} [{status}]")
        
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("\033[92m[OK] ALL ROUTES PASSED\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME ROUTES FAILED\033[0m")
        print("="*60 + "\n")
        return 1

def check_static_files():
    """Test that critical static files exist"""
    import os
    from pathlib import Path
    
    print("\n" + "="*60)
    print("STATIC ASSETS CHECK")
    print("="*60 + "\n")
    
    base_path = ROOT / 'app' / 'static'
    
    files = [
        'css/dist/main.min.css',
        'js/dist/main.min.js',
        'js/dist/disease.min.js',
        'js/dist/advisory.min.js',
    ]
    
    all_exist = True
    
    for file in files:
        full_path = base_path / file
        exists = full_path.exists()
        
        symbol = "[OK]" if exists else "[FAIL]"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {file}")
        
        if not exists:
            all_exist = False
    
    print("\n" + "="*60)
    if all_exist:
        print("\033[92m[OK] ALL STATIC ASSETS FOUND\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME STATIC ASSETS MISSING\033[0m")
        print("="*60 + "\n")
        return 1

def check_templates():
    """Test that all required templates exist"""
    from pathlib import Path
    
    print("\n" + "="*60)
    print("TEMPLATES CHECK")
    print("="*60 + "\n")
    
    base_path = ROOT / 'app' / 'templates'
    
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
        
        symbol = "[OK]" if exists else "[FAIL]"
        color = "\033[92m" if exists else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {template}")
        
        if not exists:
            all_exist = False
    
    print("\n" + "="*60)
    if all_exist:
        print("\033[92m[OK] ALL TEMPLATES FOUND\033[0m")
        print("="*60 + "\n")
        return 0
    else:
        print("\033[91m[FAIL] SOME TEMPLATES MISSING\033[0m")
        print("="*60 + "\n")
        return 1

def test_routes():
    assert check_routes() == 0, 'One or more frontend routes failed'


def test_static_files():
    assert check_static_files() == 0, 'Required assets are missing; run npm run build:all'


def test_templates():
    assert check_templates() == 0, 'Required templates are missing'


def test_navigation_is_ready_without_javascript():
    """Direct loads must include the correct desktop/mobile active links in HTML."""
    class HeaderParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_header = False
            self.headers = 0
            self.links = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'header' and attrs.get('id') == 'site-header':
                self.in_header = True
                self.headers += 1
            if self.in_header and tag == 'a' and 'data-nav-link' in attrs:
                self.links.append(attrs)

        def handle_endtag(self, tag):
            if tag == 'header':
                self.in_header = False

    client = create_app({'TESTING': True}).test_client()
    navigation = ['/', '/disease', '/advisory', '/about']
    for path, expected in [
        ('/', '/'), ('/disease', '/disease'), ('/advisory', '/advisory'),
        ('/about', '/about'), ('/disease/result', '/disease'), ('/nonexistent', None),
    ]:
        parser = HeaderParser()
        with client.get(path) as response:
            parser.feed(response.get_data(as_text=True))
        assert parser.headers == 1, path
        assert [link['href'] for link in parser.links] == navigation * 2, path
        active = [link for link in parser.links if 'active' in link.get('class', '').split()]
        assert [link['href'] for link in active] == ([expected] * 2 if expected else []), path
        assert all(link.get('aria-current') == 'page' for link in active), path
        assert all('aria-current' not in link for link in parser.links if link not in active), path


if __name__ == '__main__':
    exit_code = 0
    
    # Run all tests
    exit_code |= check_templates()
    exit_code |= check_static_files()
    exit_code |= check_routes()
    
    if exit_code == 0:
        print("\n\033[92m" + "="*60)
        print("FRONTEND INTEGRATION COMPLETE - ALL CHECKS PASSED")
        print("="*60 + "\033[0m\n")
        print("You can now run the application:")
        print("  python run.py")
        print("\nThen visit: http://127.0.0.1:5000\n")
    else:
        print("\n\033[91m" + "="*60)
        print("SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("="*60 + "\033[0m\n")
    
    sys.exit(exit_code)
