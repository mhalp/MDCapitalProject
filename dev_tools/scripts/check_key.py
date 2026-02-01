import requests
import json
import sys

def check_key(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    print(f"Checking models for key: {api_key[:10]}...")
    
    try:
        # Using verify=False because of the Etrog filter issues we've seen
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("\n✅ SUCCESS! Available models:")
            for m in models:
                if "generateContent" in m.get('supportedGenerationMethods', []):
                    print(f" - {m['name']}")
        else:
            print(f"\n❌ FAILED! Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_key.py <API_KEY>")
    else:
        check_key(sys.argv[1])
