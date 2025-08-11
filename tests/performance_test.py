import requests
import time
import threading
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np

BASE_URL = "http://127.0.0.1:8000"

class PerformanceTests:
    """Performance and load testing suite for ESS Agents API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.results = []
    
    def measure_response_time(self, query: str) -> Dict[str, Any]:
        """Measure response time for a single query"""
        start_time = time.time()
        
        try:
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            end_time = time.time()
            
            return {
                "query": query,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200,
                "response_size": len(response.text) if response.text else 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "query": query,
                "status_code": None,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e),
                "response_size": 0
            }
    
    def test_response_times(self, num_requests: int = 10):
        """Test response times for different types of queries"""
        print(f"🧪 Testing response times with {num_requests} requests...")
        
        test_queries = [
            "What is my leave balance?",
            "When will I get my salary?",
            "What is the company's leave policy?",
            "I need to apply for leave",
            "What are the working hours?",
            "How can I download my payslip?",
            "What is the dress code policy?",
            "When will I receive my Form 16?",
            "How many sick leaves do I get?",
            "I want to speak to HR"
        ]
        
        # Repeat queries to reach num_requests
        queries = (test_queries * (num_requests // len(test_queries) + 1))[:num_requests]
        
        results = []
        for i, query in enumerate(queries):
            print(f"Request {i+1}/{num_requests}: {query[:50]}...")
            result = self.measure_response_time(query)
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        
        # Calculate statistics
        response_times = [r["response_time"] for r in results if r["success"]]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        if response_times:
            stats = {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            stats = {"min": 0, "max": 0, "mean": 0, "median": 0, "std": 0}
        
        print(f"\n📊 Response Time Statistics:")
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Min: {stats['min']:.3f}s")
        print(f"Max: {stats['max']:.3f}s")
        print(f"Mean: {stats['mean']:.3f}s")
        print(f"Median: {stats['median']:.3f}s")
        print(f"Std Dev: {stats['std']:.3f}s")
        
        return results, stats
    
    def test_concurrent_load(self, num_concurrent: int = 5, num_requests: int = 20):
        """Test system performance under concurrent load"""
        print(f"🧪 Testing concurrent load: {num_concurrent} concurrent users, {num_requests} total requests...")
        
        test_queries = [
            "What is my leave balance?",
            "When will I get my salary?",
            "What is the company's leave policy?",
            "I need to apply for leave",
            "What are the working hours?"
        ]
        
        def worker(worker_id: int, num_requests_per_worker: int):
            """Worker function for concurrent testing"""
            worker_results = []
            for i in range(num_requests_per_worker):
                query = test_queries[i % len(test_queries)]
                result = self.measure_response_time(query)
                result["worker_id"] = worker_id
                result["request_id"] = i
                worker_results.append(result)
                time.sleep(0.05)  # Small delay
            return worker_results
        
        # Calculate requests per worker
        requests_per_worker = num_requests // num_concurrent
        extra_requests = num_requests % num_concurrent
        
        all_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = []
            
            # Submit tasks
            for i in range(num_concurrent):
                requests_for_this_worker = requests_per_worker + (1 if i < extra_requests else 0)
                future = executor.submit(worker, i, requests_for_this_worker)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        response_times = [r["response_time"] for r in all_results if r["success"]]
        success_rate = sum(1 for r in all_results if r["success"]) / len(all_results)
        
        if response_times:
            stats = {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            stats = {"min": 0, "max": 0, "mean": 0, "median": 0, "std": 0}
        
        print(f"\n📊 Concurrent Load Test Results:")
        print(f"Total Time: {total_time:.3f}s")
        print(f"Requests per Second: {num_requests / total_time:.2f}")
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Mean Response Time: {stats['mean']:.3f}s")
        print(f"Max Response Time: {stats['max']:.3f}s")
        
        return all_results, stats
    
    def test_memory_usage(self, num_requests: int = 50):
        """Test memory usage by making many requests and checking state size"""
        print(f"🧪 Testing memory usage with {num_requests} requests...")
        
        # Get initial state size
        initial_response = self.session.get(f"{self.base_url}/state")
        initial_state = initial_response.json()
        initial_history_size = len(initial_state.get('interaction_history', []))
        
        print(f"Initial interaction history size: {initial_history_size}")
        
        # Make many requests
        test_queries = [
            "What is my leave balance?",
            "When will I get my salary?",
            "What is the company's leave policy?"
        ]
        
        for i in range(num_requests):
            query = test_queries[i % len(test_queries)]
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/query", json=payload)
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1}/{num_requests} requests...")
        
        # Get final state size
        final_response = self.session.get(f"{self.base_url}/state")
        final_state = final_response.json()
        final_history_size = len(final_state.get('interaction_history', []))
        
        print(f"Final interaction history size: {final_history_size}")
        print(f"History growth: {final_history_size - initial_history_size} entries")
        
        return {
            "initial_size": initial_history_size,
            "final_size": final_history_size,
            "growth": final_history_size - initial_history_size
        }
    
    def test_error_recovery(self):
        """Test system recovery after errors"""
        print("🧪 Testing error recovery...")
        
        # Test with invalid requests
        invalid_payloads = [
            {"query": ""},
            {"invalid_field": "test"},
            {},
            {"query": "a" * 10000}  # Very long query
        ]
        
        error_results = []
        for payload in invalid_payloads:
            result = self.measure_response_time("test")  # We'll override the payload
            start_time = time.time()
            try:
                response = self.session.post(f"{self.base_url}/query", json=payload)
                end_time = time.time()
                error_results.append({
                    "payload": payload,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                })
            except Exception as e:
                end_time = time.time()
                error_results.append({
                    "payload": payload,
                    "status_code": None,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                })
        
        # Test normal request after errors
        print("Testing normal request after errors...")
        normal_result = self.measure_response_time("What is my leave balance?")
        
        print(f"Normal request after errors: {'SUCCESS' if normal_result['success'] else 'FAILED'}")
        
        return error_results, normal_result
    
    def test_streaming_performance(self, num_requests: int = 5):
        """Test streaming endpoint performance"""
        print(f"🧪 Testing streaming performance with {num_requests} requests...")
        
        test_queries = [
            "What is the company's leave policy?",
            "How do I apply for leave?",
            "What are the working hours?"
        ]
        
        streaming_results = []
        
        for i in range(num_requests):
            query = test_queries[i % len(test_queries)]
            print(f"Streaming request {i+1}/{num_requests}: {query}")
            
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}/query-streaming", params={"query": query})
                end_time = time.time()
                
                if response.status_code == 200:
                    # Count the number of events received
                    lines = response.text.split('\n')
                    event_count = len([line for line in lines if line.strip() and line.startswith('data:')])
                    
                    streaming_results.append({
                        "query": query,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "event_count": event_count,
                        "success": True
                    })
                else:
                    streaming_results.append({
                        "query": query,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": False
                    })
            except Exception as e:
                end_time = time.time()
                streaming_results.append({
                    "query": query,
                    "status_code": None,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate statistics
        response_times = [r["response_time"] for r in streaming_results if r["success"]]
        if response_times:
            avg_time = statistics.mean(response_times)
            print(f"Average streaming response time: {avg_time:.3f}s")
        
        return streaming_results
    
    def generate_performance_report(self, results: Dict[str, Any]):
        """Generate a comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST REPORT")
        print("=" * 60)
        
        for test_name, test_results in results.items():
            print(f"\n{test_name}:")
            if isinstance(test_results, dict) and "mean" in test_results:
                print(f"  Mean Response Time: {test_results['mean']:.3f}s")
                print(f"  Max Response Time: {test_results['max']:.3f}s")
                print(f"  Min Response Time: {test_results['min']:.3f}s")
            elif isinstance(test_results, list):
                success_count = sum(1 for r in test_results if r.get("success", False))
                print(f"  Success Rate: {success_count}/{len(test_results)} ({success_count/len(test_results):.1%})")
    
    def run_all_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Starting Performance Test Suite...")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Response times
        print("\n1. Testing Response Times...")
        response_results, response_stats = self.test_response_times(20)
        results["Response Times"] = response_stats
        
        # Test 2: Concurrent load
        print("\n2. Testing Concurrent Load...")
        concurrent_results, concurrent_stats = self.test_concurrent_load(3, 15)
        results["Concurrent Load"] = concurrent_stats
        
        # Test 3: Memory usage
        print("\n3. Testing Memory Usage...")
        memory_results = self.test_memory_usage(30)
        results["Memory Usage"] = memory_results
        
        # Test 4: Error recovery
        print("\n4. Testing Error Recovery...")
        error_results, normal_result = self.test_error_recovery()
        results["Error Recovery"] = {"error_requests": len(error_results), "normal_after_error": normal_result["success"]}
        
        # Test 5: Streaming performance
        print("\n5. Testing Streaming Performance...")
        streaming_results = self.test_streaming_performance(5)
        results["Streaming Performance"] = {"total_requests": len(streaming_results), "successful": sum(1 for r in streaming_results if r["success"])}
        
        # Generate report
        self.generate_performance_report(results)
        
        return results

def main():
    """Main function to run performance tests"""
    performance_tester = PerformanceTests()
    results = performance_tester.run_all_performance_tests()
    
    print("\n✅ Performance testing completed!")
    return results

if __name__ == "__main__":
    main() 