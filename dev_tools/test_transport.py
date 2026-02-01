from langchain_google_genai import ChatGoogleGenerativeAI
import os
import ssl

# SSL Configuration for Testing
cert_path = os.path.abspath("combined.pem")
if not os.path.exists(cert_path):
    cert_path = os.path.abspath("etrog.crt")

if os.path.exists(cert_path):
    print(f"Found custom certificate at {cert_path}. Configuring SSL...")
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = cert_path
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
elif os.environ.get('MDC_BYPASS_SSL') == '1':
    print("SSL Verification is BYPASSED (MDC_BYPASS_SSL=1)")
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key="test",
        transport="rest"
    )
    print("Success: transport='rest' is accepted")
except TypeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Other Error: {e}")
