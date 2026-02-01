import requests
import sys
import time
import subprocess
import os
import signal
sys.path.append(os.getcwd())

# Configuration
TARGETS = {
    "ecommerce": {"url": "http://localhost:5002", "app": "env/target_app_ecommerce.py", "port": 5002},
    "social":    {"url": "http://localhost:5003", "app": "env/target_app_social.py",    "port": 5003},
    "banking":   {"url": "http://localhost:5004", "app": "env/target_app_banking.py",   "port": 5004},
    "blog":      {"url": "http://localhost:5005", "app": "env/target_app_blog.py",      "port": 5005},
    "fileshare": {"url": "http://localhost:5006", "app": "env/target_app_fileshare.py", "port": 5006},
}

def start_server(name):
    config = TARGETS[name]
    print(f"🚀 Starting {name} on port {config['port']}...")
    # Use Popen to start independently
    cwd = os.getcwd()
    # Windows python usage
    cmd = [sys.executable, config["app"]]
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Wait for startup
    return p

def stop_server(process):
    try:
        process.terminate()
        process.wait() # Windows specific
    except:
        pass

def test_xss_generic(url, method="POST", endpoint="", param_name="content", extra_data={}, use_json=False, session=None, allow_redirects=True):
    print(f"   🧪 Testing XSS on {url}{endpoint}...")
    success_count = 0
    # Test a subset of payloads to be fast
    test_payloads = [
        "<script>alert(1)</script>", 
        "<svg/onload=alert(1)>", 
        "<img src=x onerror=alert(1)>"
    ]
    
    s = session if session else requests.Session()
    
    for payload in test_payloads:
        data = extra_data.copy()
        data[param_name] = payload
        
        try:
            if method == "POST":
                if use_json:
                    r = s.post(f"{url}{endpoint}", json=data, timeout=2, allow_redirects=allow_redirects)
                else:
                    r = s.post(f"{url}{endpoint}", data=data, timeout=2, allow_redirects=allow_redirects)
            else:
                r = s.get(f"{url}{endpoint}", params=data, timeout=2, allow_redirects=allow_redirects)
                
            if "X-Vuln-Confirmed" in r.headers:
                print(f"     ✅ Verified: {payload[:30]}...")
                success_count += 1
            else:
                print(f"     ❌ FAILED: {payload[:30]}... Status: {r.status_code}")
        except Exception as e:
            print(f"     ⚠️ Error: {e}")
            
    return success_count == len(test_payloads)

def verify_ecommerce():
    s = requests.Session()
    url = TARGETS["ecommerce"]["url"]
    # Register/Login first
    try:
        s.post(f"{url}/register", data={"username": "tester", "password": "pw", "email": "t@t.com"})
        s.post(f"{url}/login", data={"username": "tester", "password": "pw"})
    except:
        pass 
    return test_xss_generic(url, endpoint="/api/posts", param_name="content", extra_data={"title": "Test"}, use_json=True, session=s)

def verify_social():
    # Needs login first
    s = requests.Session()
    url = TARGETS["social"]["url"]
    s.post(f"{url}/register", data={"username": "tester", "email": "t@t.com", "password": "pw"})
    s.post(f"{url}/login", data={"username": "tester", "password": "pw"})
    
    # Post creation - Check redirect response for header
    print(f"   🧪 Testing XSS on {url}/posts...")
    payload = "<svg/onload=alert(1)>"
    # IMPORTANT: Social app redirects on success. The header is on the 302 response.
    r = s.post(f"{url}/posts", data={"content": payload}, allow_redirects=False)
    
    if "X-Vuln-Confirmed" in r.headers:
        print(f"     ✅ Verified Social Post XSS")
        return True
    else:
        print(f"     ❌ FAILED Social Post XSS. Status: {r.status_code}")
        # Debug info
        if r.status_code != 302:
            print(f"     Debug: Got {r.status_code} response instead of redirect.")
        return False

def verify_blog():
    # Reflected XSS
    url = TARGETS["blog"]["url"]
    return test_xss_generic(url, method="GET", endpoint="/", param_name="search", extra_data={})

def verify_banking():
    s = requests.Session()
    url = TARGETS["banking"]["url"]
    # Login
    s.post(f"{url}/login", data={"username": "admin", "password": "admin123"})
    
    # Test XSS in Transfer Description
    return test_xss_generic(url, endpoint="/transfer", param_name="description", 
                           extra_data={"to_account": "1002", "amount": "1"}, session=s, allow_redirects=False)

def verify_fileshare():
    s = requests.Session()
    url = TARGETS["fileshare"]["url"]
    # Register/Login
    s.post(f"{url}/register", data={"username": "tester", "password": "pw"})
    s.post(f"{url}/login", data={"username": "tester", "password": "pw"})
    
    print(f"   🧪 Testing XSS on {url}/upload...")
    # Test Stored XSS via File Description
    success_count = 0
    test_payloads = ["<script>alert(1)</script>", "<svg/onload=alert(1)>"]
    
    for payload in test_payloads:
        # Need to send a real-ish file for upload
        files = {'file': ('test.txt', 'hello world')}
        data = {'description': payload}
        r = s.post(f"{url}/upload", files=files, data=data, allow_redirects=False)
        
        if "X-Vuln-Confirmed" in r.headers:
            print(f"     ✅ Verified: {payload[:30]}...")
            success_count += 1
        else:
            print(f"     ❌ FAILED: {payload[:30]}... Status: {r.status_code}")
            
    return success_count == len(test_payloads)

def run_all():
    results = {}
    
    for name in TARGETS.keys():
        p = start_server(name)
        try:
            if name == "ecommerce": results[name] = verify_ecommerce()
            elif name == "social":   results[name] = verify_social()
            elif name == "blog":     results[name] = verify_blog()
            elif name == "banking":  results[name] = verify_banking()
            elif name == "fileshare": results[name] = verify_fileshare()
        except Exception as e:
            print(f"  ❌ Error verifying {name}: {e}")
            results[name] = False
        finally:
            stop_server(p)
        
    print("\n📊 Final Verification Results:")
    all_pass = True
    for name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {name.upper():<10}: {status}")
        if not success: all_pass = False
        
    if all_pass:
        print("\n✅ ALL SYSTEMS READY FOR TRAINING!")
    else:
        print("\n⚠️ SOME SYSTEMS FAILED VERIFICATION.")
        
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    run_all()
