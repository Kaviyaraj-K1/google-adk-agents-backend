import requests

BASE_URL = "http://127.0.0.1:8000"

def test_query():
    payload = {"query": "Hello, what is the policy for health insurance?"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print("Query Response:", response.status_code, response.json())

def test_state():
    response = requests.get(f"{BASE_URL}/state")
    print("State Response:", response.status_code, response.json())

if __name__ == "__main__":
    print("🚀 Testing /query endpoint...")
    test_query()

    print("\n🚀 Testing /state endpoint...")
    test_state()
