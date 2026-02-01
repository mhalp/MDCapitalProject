import os
import google.generativeai as genai

# SSL Configuration
cert_path = os.path.abspath("combined.pem")
if os.path.exists(cert_path):
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = cert_path
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path

api_key = "AIzaSyAKhF0BEvsIcArojfQ246ubsxoIbclK4gY"
genai.configure(api_key=api_key)

print("Listing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
