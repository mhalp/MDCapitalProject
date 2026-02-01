import requests
import certifi
import os
import ssl
import socket

def debug_ssl(url="https://google.com"):
    print("--- SSL Debugging Tool ---")
    
    # 1. Check Environment Variables
    print(f"\n[1] Environment Variables:")
    print(f"REQUESTS_CA_BUNDLE: {os.environ.get('REQUESTS_CA_BUNDLE', 'Not Set')}")
    print(f"SSL_CERT_FILE: {os.environ.get('SSL_CERT_FILE', 'Not Set')}")
    print(f"CURL_CA_BUNDLE: {os.environ.get('CURL_CA_BUNDLE', 'Not Set')}")

    # 2. Check Certifi
    print(f"\n[2] Certifi Bundle Path:")
    try:
        print(f"Path: {certifi.where()}")
    except Exception as e:
        print(f"Error getting certifi path: {e}")

    # 3. Check Python Default Verify Paths
    print(f"\n[3] Python Default Verify Paths:")
    try:
        paths = ssl.get_default_verify_paths()
        print(f"CAfile: {paths.cafile}")
        print(f"CApath: {paths.capath}")
        print(f"Openssl CAfile: {paths.openssl_cafile}")
        print(f"Openssl CApath: {paths.openssl_capath}")
    except Exception as e:
        print(f"Error getting default verify paths: {e}")

    # 4. Attempt Connection with Requests
    print(f"\n[4] Attempting requests.get('{url}'):")
    try:
        r = requests.get(url, timeout=5)
        print(f"SUCCESS! Status Code: {r.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"FAILED with SSLError: {e}")
    except Exception as e:
        print(f"FAILED with other error: {e}")

    # 5. Deep SSL Inspection
    print(f"\n[5] Deep SSL Inspection (socket level):")
    hostname = url.replace("https://", "").split("/")[0]
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"SSL Version: {ssock.version()}")
                cert = ssock.getpeercert()
                print(f"Certificate Subject: {cert.get('subject')}")
                print(f"Certificate Issuer: {cert.get('issuer')}")
    except Exception as e:
        print(f"Socket SSL Error: {e}")

if __name__ == "__main__":
    debug_ssl()
