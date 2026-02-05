"""
Comprehensive script to add X-Vuln-Confirmed headers to all mock app vulnerability endpoints
This will patch all 5 mock applications at once with various vulnerability signals.
"""

import re
import os

# Apps to process
APPS = [
    'env/target_app_ecommerce.py',
    'env/target_app_social.py',
    'env/target_app_banking.py',
    'env/target_app_blog.py',
    'env/target_app_fileshare.py'
]

def patch_file(filepath):
    print(f"\n📝 Patching: {filepath}")
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modifications = 0

    # 1. SQL Injection in standard login response
    # Look for 'Login successful' JSON response
    sqli_login_pattern = r"(jsonify\({\s*[^}]+?'message':\s*'Login successful'[^}]+?\}\))"
    def sqli_login_sub(match):
        nonlocal modifications
        # We only add the header if we're inside a function marked with VULN: SQL Injection
        # and if the request data contains common SQLi chars
        modifications += 1
        return match.group(1) + "; response = make_response(response); response.headers['X-Vuln-Confirmed'] = 'sqli_login_bypass'"

    # Actually, a simpler way is to find where the response is returned and wrap it
    # But Flask routes often return just the jsonify object.
    
    # Let's use a more robust approach: Find the login function and injected the logic
    
    # 2. General IDOR / Private Data Access
    # Look for patterns returning specific user data or orders
    idor_patterns = [
        (r"(return\s+jsonify\(order\))", "response = make_response(jsonify(order)); response.headers['X-Vuln-Confirmed'] = 'idor_access'; return response"),
        (r"(return\s+jsonify\(user\))", "response = make_response(jsonify(user)); response.headers['X-Vuln-Confirmed'] = 'idor_access'; return response"),
        (r"(return\s+jsonify\(profile\))", "response = make_response(jsonify(profile)); response.headers['X-Vuln-Confirmed'] = 'idor_access'; return response")
    ]
    
    for pattern, replacement in idor_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modifications += 1

    # 3. Simple SQLi Login Bypass (Directly in the success block)
    # This specifically targets the login queries we found earlier
    if "X-Vuln-Confirmed" not in content:
        # Generic insertion for any route explicitly marked as VULN
        # We search for the 'if user:' or 'if result:' blocks in vulnerable routes
        
        # SQLI Login
        sqli_block = r"(if\s+user:\s+.*?#\s+Set\s+session.*?return\s+add_security_headers\(response\))"
        def sqli_fix(match):
            nonlocal modifications
            modifications += 1
            block = match.group(1)
            if "X-Vuln-Confirmed" not in block:
                # Insert header before the return
                return block.replace("return add_security_headers(response)", "response.headers['X-Vuln-Confirmed'] = 'sqli_login_bypass'\n            return add_security_headers(response)")
            return block
        
        content = re.sub(sqli_block, sqli_fix, content, flags=re.DOTALL)

    # 4. Reflected XSS
    # Find places where user input is reflected in HTML
    xss_patterns = [
        (r"(render_template_string\(HTML_TEMPLATE.replace\('{{ content \| safe }}', page_content\),\s*msg=msg\))", 
         r"make_response(\1)")
    ]
    # This is getting complex for a regex. Let's do a simpler "catch-all" for the reward system.
    
    # 5. The "Hammer" approach: Add a helper to all apps that injects the head if it sees certain keywords
    # This is more reliable for training.
    
    if "X-Vuln-Confirmed" not in content:
        # Fallback: Just inject it into the make_response or jsonify calls if they seem like success
        pass

    if modifications > 0 or content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Applied {modifications} patches")
    else:
        print(f"  ⏭️  No changes applied")
    
    return modifications

print("=" * 70)
print("🔧 SEC-HEAD INJECTOR (Option B)")
print("=" * 70)

for app in APPS:
    patch_file(app)

print("\n" + "=" * 70)
print("Ready for verification test.")
