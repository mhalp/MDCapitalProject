import requests
import os

cert_path = os.path.abspath("combined.pem")
os.environ['REQUESTS_CA_BUNDLE'] = cert_path
print(f"Testing SSL with cert: {cert_path}")

try:
    r = requests.get("https://generativelanguage.googleapis.com", timeout=5)
    print(f"Success! Status: {r.status_code}")
except Exception as e:
    print(f"Failed: {e}")
