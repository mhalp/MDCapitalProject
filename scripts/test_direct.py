import google.generativeai as genai
import sys
import os

def test_direct(api_key):
    print(f"Testing direct Google GenAI SDK with key: {api_key[:10]}...")
    
    # Bypass SSL for the SDK
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''
    
    genai.configure(api_key=api_key)
    
    # Try different model names
    models_to_try = ["gemini-1.5-flash", "gemini-pro-latest", "gemini-flash-latest"]
    
    for model_name in models_to_try:
        print(f"\nTrying model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"✅ SUCCESS! Response: {response.text}")
            return # Stop if one works
        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_direct.py <API_KEY>")
    else:
        test_direct(sys.argv[1])
