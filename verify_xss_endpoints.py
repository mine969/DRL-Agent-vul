import sys
import os

# Add the env directory to path so we can import target_app_ecommerce
sys.path.append(os.path.join(os.getcwd(), 'env'))

from target_app_ecommerce import app

def test_xss_endpoints():
    client = app.test_client()
    
    print("Testing /api/posts XSS...")
    response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': '<script>alert(1)</script>'
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200 and response.headers.get('X-Vuln-Confirmed') == 'xss_stored_posts_success':
        print("SUCCESS: /api/posts vulnerability confirmed!")
    else:
        print("FAILURE: /api/posts vulnerability NOT detected.")

    print("\nTesting /api/posts/1/comments XSS...")
    response = client.post('/api/posts/1/comments', json={
        'content': '<script>alert(1)</script>'
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200 and response.headers.get('X-Vuln-Confirmed') == 'xss_stored_comments_success':
        print("SUCCESS: /api/posts/1/comments vulnerability confirmed!")
    else:
        print("FAILURE: /api/posts/1/comments vulnerability NOT detected.")

if __name__ == '__main__':
    test_xss_endpoints()
