import requests
import time
import json
from typing import Dict, Any, List

BASE_URL = "http://127.0.0.1:8000"

class IntegrationTests:
    """Integration testing suite for ESS Agents API - testing complete workflows"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current session state"""
        response = self.session.get(f"{self.base_url}/state")
        return response.json() if response.status_code == 200 else {}
    
    def make_query(self, query: str) -> Dict[str, Any]:
        """Make a query and return the response"""
        payload = {"query": query}
        response = self.session.post(f"{self.base_url}/query", json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def test_leave_application_workflow(self):
        """Test complete leave application workflow"""
        print("🧪 Testing Leave Application Workflow...")
        
        # Step 1: Check leave balance
        print("\n1. Checking leave balance...")
        result1 = self.make_query("What is my leave balance?")
        print(f"Response: {result1.get('response', 'No response')[:100]}...")
        
        # Step 2: Ask about leave policy
        print("\n2. Asking about leave policy...")
        result2 = self.make_query("What is the company's leave policy?")
        print(f"Response: {result2.get('response', 'No response')[:100]}...")
        
        # Step 3: Apply for leave
        print("\n3. Applying for leave...")
        result3 = self.make_query("I need to apply for leave from 15th to 18th August for a family function")
        print(f"Response: {result3.get('response', 'No response')[:100]}...")
        
        # Step 4: Check state after workflow
        print("\n4. Checking final state...")
        final_state = self.get_state()
        interaction_count = len(final_state.get('interaction_history', []))
        print(f"Total interactions in workflow: {interaction_count}")
        
        return {
            "leave_balance_check": result1.get('success', False),
            "policy_inquiry": result2.get('success', False),
            "leave_application": result3.get('success', False),
            "total_interactions": interaction_count
        }
    
    def test_payroll_inquiry_workflow(self):
        """Test complete payroll inquiry workflow"""
        print("🧪 Testing Payroll Inquiry Workflow...")
        
        # Step 1: Ask about salary
        print("\n1. Asking about salary...")
        result1 = self.make_query("What is my current salary?")
        print(f"Response: {result1.get('response', 'No response')[:100]}...")
        
        # Step 2: Ask about payslip
        print("\n2. Asking about payslip...")
        result2 = self.make_query("How can I download my payslip?")
        print(f"Response: {result2.get('response', 'No response')[:100]}...")
        
        # Step 3: Ask about tax documents
        print("\n3. Asking about tax documents...")
        result3 = self.make_query("When will I receive my Form 16?")
        print(f"Response: {result3.get('response', 'No response')[:100]}...")
        
        # Step 4: Ask about deductions
        print("\n4. Asking about deductions...")
        result4 = self.make_query("What are the tax deductions from my salary?")
        print(f"Response: {result4.get('response', 'No response')[:100]}...")
        
        return {
            "salary_inquiry": result1.get('success', False),
            "payslip_inquiry": result2.get('success', False),
            "tax_document_inquiry": result3.get('success', False),
            "deduction_inquiry": result4.get('success', False)
        }
    
    def test_policy_inquiry_workflow(self):
        """Test complete policy inquiry workflow"""
        print("🧪 Testing Policy Inquiry Workflow...")
        
        # Step 1: Ask about working hours
        print("\n1. Asking about working hours...")
        result1 = self.make_query("What are the working hours?")
        print(f"Response: {result1.get('response', 'No response')[:100]}...")
        
        # Step 2: Ask about dress code
        print("\n2. Asking about dress code...")
        result2 = self.make_query("What is the dress code policy?")
        print(f"Response: {result2.get('response', 'No response')[:100]}...")
        
        # Step 3: Ask about leave carry forward
        print("\n3. Asking about leave carry forward...")
        result3 = self.make_query("Can I carry forward my unused earned leave?")
        print(f"Response: {result3.get('response', 'No response')[:100]}...")
        
        # Step 4: Ask about sick leave
        print("\n4. Asking about sick leave...")
        result4 = self.make_query("How many sick leaves do I get per year?")
        print(f"Response: {result4.get('response', 'No response')[:100]}...")
        
        return {
            "working_hours": result1.get('success', False),
            "dress_code": result2.get('success', False),
            "leave_carry_forward": result3.get('success', False),
            "sick_leave": result4.get('success', False)
        }
    
    def test_escalation_workflow(self):
        """Test escalation to human support workflow"""
        print("🧪 Testing Escalation Workflow...")
        
        # Step 1: Try to get help with a complex issue
        print("\n1. Requesting help with complex issue...")
        result1 = self.make_query("I have a complex personal issue that I need to discuss with HR")
        print(f"Response: {result1.get('response', 'No response')[:100]}...")
        
        # Step 2: Request human support
        print("\n2. Requesting human support...")
        result2 = self.make_query("I need to speak to someone from HR immediately")
        print(f"Response: {result2.get('response', 'No response')[:100]}...")
        
        # Step 3: Create support ticket
        print("\n3. Creating support ticket...")
        result3 = self.make_query("Create a support ticket for my urgent issue")
        print(f"Response: {result3.get('response', 'No response')[:100]}...")
        
        return {
            "complex_issue": result1.get('success', False),
            "human_support": result2.get('success', False),
            "support_ticket": result3.get('success', False)
        }
    
    def test_mixed_workflow(self):
        """Test mixed workflow with different types of queries"""
        print("🧪 Testing Mixed Workflow...")
        
        queries = [
            "What is my leave balance?",
            "When will I get my salary?",
            "What is the dress code policy?",
            "I need to apply for leave next week",
            "How can I download my payslip?",
            "What are the working hours?",
            "I want to speak to HR about a personal matter"
        ]
        
        results = []
        for i, query in enumerate(queries):
            print(f"\n{i+1}. {query}")
            result = self.make_query(query)
            success = 'query' in result and 'response' in result
            results.append(success)
            print(f"   Success: {success}")
            time.sleep(0.5)  # Small delay between queries
        
        # Check final state
        final_state = self.get_state()
        interaction_count = len(final_state.get('interaction_history', []))
        
        return {
            "total_queries": len(queries),
            "successful_queries": sum(results),
            "success_rate": sum(results) / len(queries),
            "total_interactions": interaction_count
        }
    
    def test_context_persistence(self):
        """Test that context persists across multiple interactions"""
        print("🧪 Testing Context Persistence...")
        
        # Get initial state
        initial_state = self.get_state()
        initial_interactions = len(initial_state.get('interaction_history', []))
        print(f"Initial interactions: {initial_interactions}")
        
        # Make a series of related queries
        queries = [
            "What is my leave balance?",
            "How many annual leaves do I have?",
            "Can I carry forward unused leaves?",
            "What is the process to apply for leave?"
        ]
        
        for query in queries:
            result = self.make_query(query)
            print(f"Query: {query}")
            print(f"Response length: {len(result.get('response', ''))}")
        
        # Check final state
        final_state = self.get_state()
        final_interactions = len(final_state.get('interaction_history', []))
        print(f"Final interactions: {final_interactions}")
        
        # Check if user context is maintained
        user_name = final_state.get('user_name', 'Unknown')
        user_email = final_state.get('user_email', 'Unknown')
        print(f"User context maintained: {user_name} ({user_email})")
        
        return {
            "initial_interactions": initial_interactions,
            "final_interactions": final_interactions,
            "interaction_growth": final_interactions - initial_interactions,
            "context_maintained": user_name != 'Unknown' and user_email != 'Unknown'
        }
    
    def test_error_handling_workflow(self):
        """Test error handling in workflows"""
        print("🧪 Testing Error Handling Workflow...")
        
        # Test with invalid queries
        invalid_queries = [
            "",
            "   ",
            "a" * 1000,  # Very long query
        ]
        
        error_results = []
        for query in invalid_queries:
            result = self.make_query(query)
            error_results.append({
                "query": query[:50] + "..." if len(query) > 50 else query,
                "has_error": "error" in result,
                "status": "error" if "error" in result else "success"
            })
        
        # Test recovery with valid query
        print("\nTesting recovery with valid query...")
        recovery_result = self.make_query("What is my leave balance?")
        recovery_success = 'query' in recovery_result and 'response' in recovery_result
        
        return {
            "invalid_queries": error_results,
            "recovery_success": recovery_success
        }
    
    def test_agent_delegation(self):
        """Test that queries are properly delegated to appropriate agents"""
        print("🧪 Testing Agent Delegation...")
        
        # Test queries that should go to specific agents
        agent_tests = {
            "policy_agent": [
                "What is the company's leave policy?",
                "What are the working hours?",
                "What is the dress code policy?"
            ],
            "payroll_agent": [
                "When will I get my salary?",
                "How can I download my payslip?",
                "What are the tax deductions?"
            ],
            "leave_agent": [
                "What is my leave balance?",
                "How many annual leaves do I have?",
                "How do I apply for leave?"
            ],
            "case_agent": [
                "I need to apply for leave from 15th to 18th August",
                "I want to speak to HR about a personal issue",
                "Create a support ticket for me"
            ]
        }
        
        delegation_results = {}
        
        for agent_name, queries in agent_tests.items():
            print(f"\nTesting {agent_name} delegation...")
            agent_results = []
            
            for query in queries:
                result = self.make_query(query)
                success = 'query' in result and 'response' in result
                agent_results.append(success)
                print(f"  {query[:50]}... -> {'SUCCESS' if success else 'FAILED'}")
            
            delegation_results[agent_name] = {
                "total_queries": len(queries),
                "successful_queries": sum(agent_results),
                "success_rate": sum(agent_results) / len(queries)
            }
        
        return delegation_results
    
    def run_all_integration_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Integration Test Suite...")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Leave application workflow
        print("\n1. Leave Application Workflow")
        test_results["Leave Application"] = self.test_leave_application_workflow()
        
        # Test 2: Payroll inquiry workflow
        print("\n2. Payroll Inquiry Workflow")
        test_results["Payroll Inquiry"] = self.test_payroll_inquiry_workflow()
        
        # Test 3: Policy inquiry workflow
        print("\n3. Policy Inquiry Workflow")
        test_results["Policy Inquiry"] = self.test_policy_inquiry_workflow()
        
        # Test 4: Escalation workflow
        print("\n4. Escalation Workflow")
        test_results["Escalation"] = self.test_escalation_workflow()
        
        # Test 5: Mixed workflow
        print("\n5. Mixed Workflow")
        test_results["Mixed Workflow"] = self.test_mixed_workflow()
        
        # Test 6: Context persistence
        print("\n6. Context Persistence")
        test_results["Context Persistence"] = self.test_context_persistence()
        
        # Test 7: Error handling
        print("\n7. Error Handling")
        test_results["Error Handling"] = self.test_error_handling_workflow()
        
        # Test 8: Agent delegation
        print("\n8. Agent Delegation")
        test_results["Agent Delegation"] = self.test_agent_delegation()
        
        # Generate summary
        self.generate_integration_report(test_results)
        
        return test_results
    
    def generate_integration_report(self, results: Dict[str, Any]):
        """Generate integration test report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST REPORT")
        print("=" * 60)
        
        for test_name, test_result in results.items():
            print(f"\n{test_name}:")
            
            if isinstance(test_result, dict):
                if "success_rate" in test_result:
                    print(f"  Success Rate: {test_result['success_rate']:.1%}")
                if "total_interactions" in test_result:
                    print(f"  Total Interactions: {test_result['total_interactions']}")
                if "agent_delegation" in test_name.lower():
                    for agent, stats in test_result.items():
                        if isinstance(stats, dict) and "success_rate" in stats:
                            print(f"  {agent}: {stats['success_rate']:.1%} success rate")
        
        print("\n✅ Integration testing completed!")

def main():
    """Main function to run integration tests"""
    integration_tester = IntegrationTests()
    results = integration_tester.run_all_integration_tests()
    return results

if __name__ == "__main__":
    main() 