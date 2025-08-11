#!/usr/bin/env python3
"""
Test Runner for ESS Agents API
Runs functional, performance, and integration tests
"""

import sys
import argparse
import time
from typing import Dict, Any

# Import test modules
from test import ESSAgentTests
from performance_test import PerformanceTests
from integration_test import IntegrationTests

def run_functional_tests() -> Dict[str, Any]:
    """Run functional tests"""
    print("🚀 Running Functional Tests...")
    print("=" * 50)
    
    test_suite = ESSAgentTests()
    test_suite.run_all_tests()
    
    return {"type": "functional", "status": "completed"}

def run_performance_tests() -> Dict[str, Any]:
    """Run performance tests"""
    print("🚀 Running Performance Tests...")
    print("=" * 50)
    
    performance_tester = PerformanceTests()
    results = performance_tester.run_all_performance_tests()
    
    return {"type": "performance", "status": "completed", "results": results}

def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests"""
    print("🚀 Running Integration Tests...")
    print("=" * 50)
    
    integration_tester = IntegrationTests()
    results = integration_tester.run_all_integration_tests()
    
    return {"type": "integration", "status": "completed", "results": results}

def run_all_tests() -> Dict[str, Any]:
    """Run all test suites"""
    print("🚀 Running All Test Suites...")
    print("=" * 60)
    
    all_results = {}
    
    # Run functional tests
    print("\n1️⃣ FUNCTIONAL TESTS")
    print("-" * 30)
    all_results["functional"] = run_functional_tests()
    
    # Run performance tests
    print("\n2️⃣ PERFORMANCE TESTS")
    print("-" * 30)
    all_results["performance"] = run_performance_tests()
    
    # Run integration tests
    print("\n3️⃣ INTEGRATION TESTS")
    print("-" * 30)
    all_results["integration"] = run_integration_tests()
    
    # Generate final summary
    generate_final_summary(all_results)
    
    return all_results

def generate_final_summary(results: Dict[str, Any]):
    """Generate a final summary of all test results"""
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 60)
    
    for test_type, result in results.items():
        print(f"\n{test_type.upper()} TESTS:")
        print(f"  Status: {result.get('status', 'unknown')}")
        
        if 'results' in result:
            print(f"  Results: Available")
    
    print(f"\n✅ All test suites completed!")
    print("=" * 60)

def check_server_status() -> bool:
    """Check if the server is running"""
    import requests
    
    try:
        response = requests.get("http://127.0.0.1:8000/state", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function to run tests based on command line arguments"""
    parser = argparse.ArgumentParser(description="ESS Agents API Test Runner")
    parser.add_argument(
        "--type", 
        choices=["functional", "performance", "integration", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--check-server",
        action="store_true",
        help="Check if server is running before tests"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check server status if requested
    if args.check_server:
        print("🔍 Checking server status...")
        if not check_server_status():
            print("❌ Server is not running at http://127.0.0.1:8000")
            print("Please start the server first with: python main.py")
            sys.exit(1)
        else:
            print("✅ Server is running")
    
    # Run tests based on type
    start_time = time.time()
    
    try:
        if args.type == "functional":
            results = run_functional_tests()
        elif args.type == "performance":
            results = run_performance_tests()
        elif args.type == "integration":
            results = run_integration_tests()
        else:  # all
            results = run_all_tests()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️  Total test time: {total_time:.2f} seconds")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 