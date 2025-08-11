import requests
import json
import time
import unittest
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

class ESSAgentTests:
    """Comprehensive test suite for ESS Agents API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
    
    def test_basic_query(self):
        """Test basic query functionality"""
        print("🧪 Testing basic query...")
        payload = {"query": "Hello, what is the capital of India?"}
        response = self.session.post(f"{self.base_url}/query", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    
    def test_policy_queries(self):
        """Test policy-related queries"""
        print("\n🧪 Testing policy queries...")
        
        policy_queries = [
            "What is the company's leave policy?",
            "Can I carry forward my unused earned leave?",
            "What are the working hours?",
            "What is the dress code policy?",
            "How many sick leaves do I get per year?"
        ]
        
        for query in policy_queries:
            print(f"\nTesting: {query}")
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Agent: {result.get('progress', ['No progress'])[0] if result.get('progress') else 'No progress'}")
            else:
                print(f"Error: {response.text}")
    
    def test_payroll_queries(self):
        """Test payroll-related queries"""
        print("\n🧪 Testing payroll queries...")
        
        payroll_queries = [
            "When will I get my salary?",
            "What is my current salary?",
            "When will I receive my Form 16?",
            "What are the tax deductions from my salary?",
            "How can I download my payslip?"
        ]
        
        for query in payroll_queries:
            print(f"\nTesting: {query}")
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Agent: {result.get('progress', ['No progress'])[0] if result.get('progress') else 'No progress'}")
            else:
                print(f"Error: {response.text}")
    
    def test_leave_management_queries(self):
        """Test leave management queries"""
        print("\n🧪 Testing leave management queries...")
        
        leave_queries = [
            "What is my leave balance?",
            "How many annual leaves do I have?",
            "Can I check my sick leave balance?",
            "What types of leaves are available?",
            "How do I apply for leave?"
        ]
        
        for query in leave_queries:
            print(f"\nTesting: {query}")
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Agent: {result.get('progress', ['No progress'])[0] if result.get('progress') else 'No progress'}")
            else:
                print(f"Error: {response.text}")
    
    def test_case_management_queries(self):
        """Test case management and ticket creation"""
        print("\n🧪 Testing case management queries...")
        
        case_queries = [
            "I need to apply for leave from 15th to 18th August",
            "I want to speak to HR about a personal issue",
            "Create a support ticket for me",
            "I have an urgent issue that needs immediate attention",
            "None of the automated responses are helping, I need human support"
        ]
        
        for query in case_queries:
            print(f"\nTesting: {query}")
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Agent: {result.get('progress', ['No progress'])[0] if result.get('progress') else 'No progress'}")
            else:
                print(f"Error: {response.text}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing edge cases...")
        
        edge_cases = [
            {"query": ""},  # Empty query
            {"query": "   "},  # Whitespace only
            {"query": "a" * 1000},  # Very long query
            {"invalid_field": "test"},  # Invalid payload
            {},  # Empty payload
        ]
        
        for i, payload in enumerate(edge_cases):
            print(f"\nTesting edge case {i+1}: {payload}")
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    
    def test_out_of_scope_queries(self):
        """Test queries that should be out of scope"""
        print("\n🧪 Testing out-of-scope queries...")
        
        out_of_scope_queries = [
            "What's the weather like today?",
            "Tell me a joke",
            "Who won the World Cup?",
            "What's the best restaurant in town?",
            "How do I cook pasta?"
        ]
        
        for query in out_of_scope_queries:
            print(f"\nTesting: {query}")
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')[:100]}...")
            else:
                print(f"Error: {response.text}")
    
    def test_state_endpoint(self):
        """Test the state endpoint"""
        print("\n🧪 Testing state endpoint...")
        response = self.session.get(f"{self.base_url}/state")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            state = response.json()
            print(f"User: {state.get('user_name', 'Unknown')}")
            print(f"Email: {state.get('user_email', 'Unknown')}")
            print(f"Interaction History Count: {len(state.get('interaction_history', []))}")
        else:
            print(f"Error: {response.text}")
    
    def test_streaming_endpoint(self):
        """Test the streaming endpoint"""
        print("\n🧪 Testing streaming endpoint...")
        query = "What is the company's leave policy?"
        response = self.session.get(f"{self.base_url}/query-streaming", params={"query": query})
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Read a few lines from the stream
            lines = response.text.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"Stream: {line}")
        else:
            print(f"Error: {response.text}")
    
    def test_concurrent_queries(self):
        """Test handling multiple concurrent queries"""
        print("\n🧪 Testing concurrent queries...")
        import threading
        
        def make_query(query, thread_id):
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            print(f"Thread {thread_id}: Status {response.status_code}")
        
        queries = [
            "What is my leave balance?",
            "When will I get my salary?",
            "What is the dress code policy?",
            "I need to apply for leave"
        ]
        
        threads = []
        for i, query in enumerate(queries):
            thread = threading.Thread(target=make_query, args=(query, i+1))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print("Concurrent queries completed")
    
    def test_session_persistence(self):
        """Test that session state persists across queries"""
        print("\n🧪 Testing session persistence...")
        
        # Get initial state
        initial_response = self.session.get(f"{self.base_url}/state")
        initial_state = initial_response.json()
        initial_history_count = len(initial_state.get('interaction_history', []))
        print(f"Initial interaction history count: {initial_history_count}")
        
        # Make a query
        payload = {"query": "What is my leave balance?"}
        response = self.session.post(f"{self.base_url}/query", json=payload)
        
        # Get state after query
        final_response = self.session.get(f"{self.base_url}/state")
        final_state = final_response.json()
        final_history_count = len(final_state.get('interaction_history', []))
        print(f"Final interaction history count: {final_history_count}")
        
        # Check if history was updated
        if final_history_count > initial_history_count:
            print("✅ Session persistence working - history was updated")
            return True
        else:
            print("❌ Session persistence failed - history not updated")
            return False
    
    def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting comprehensive ESS Agents test suite...")
        print("=" * 60)
        
        tests = [
            ("Basic Query", self.test_basic_query),
            ("Policy Queries", self.test_policy_queries),
            ("Payroll Queries", self.test_payroll_queries),
            ("Leave Management", self.test_leave_management_queries),
            ("Case Management", self.test_case_management_queries),
            ("Edge Cases", self.test_edge_cases),
            ("Out of Scope", self.test_out_of_scope_queries),
            ("State Endpoint", self.test_state_endpoint),
            ("Streaming Endpoint", self.test_streaming_endpoint),
            ("Concurrent Queries", self.test_concurrent_queries),
            ("Session Persistence", self.test_session_persistence),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, "PASS" if result else "FAIL"))
            except Exception as e:
                print(f"❌ Error in {test_name}: {e}")
                results.append((test_name, "ERROR"))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        for test_name, status in results:
            print(f"{test_name:<25} {status}")
        
        passed = sum(1 for _, status in results if status == "PASS")
        total = len(results)
        print(f"\nPassed: {passed}/{total} tests")

def test_query():
    """Simple test function for backward compatibility"""
    payload = {"query": "Hello, what is the capital of India?"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print("Query Response:", response.status_code, response.json())

def test_state():
    """Simple test function for backward compatibility"""
    response = requests.get(f"{BASE_URL}/state")
    print("State Response:", response.status_code, response.json())

if __name__ == "__main__":
    # Run comprehensive test suite
    test_suite = ESSAgentTests()
    test_suite.run_all_tests()
    
    # Also run simple tests for backward compatibility
    print("\n" + "=" * 60)
    print("🔧 Running simple tests for backward compatibility...")
    print("🚀 Testing /query endpoint...")
    test_query()
    print("\n🚀 Testing /state endpoint...")
    test_state()
