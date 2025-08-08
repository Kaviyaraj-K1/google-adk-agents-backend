# ESS Agents API Test Suite

This directory contains comprehensive tests for the ESS Agents API system. The test suite is designed to validate functionality, performance, and integration aspects of the multi-agent system.

## Test Files Overview

### 1. `test.py` - Functional Tests
**Purpose**: Basic functionality testing of individual API endpoints and agent responses.

**Tests Include**:
- Basic query functionality
- Policy-related queries (leave policy, working hours, dress code, etc.)
- Payroll-related queries (salary, payslips, tax documents, etc.)
- Leave management queries (balance, application, etc.)
- Case management queries (ticket creation, escalation)
- Edge cases (empty queries, invalid payloads, etc.)
- Out-of-scope queries (weather, jokes, etc.)
- State endpoint testing
- Streaming endpoint testing
- Concurrent query handling
- Session persistence

**Usage**:
```bash
python test.py
```

### 2. `performance_test.py` - Performance & Load Tests
**Purpose**: Performance testing under various load conditions and stress scenarios.

**Tests Include**:
- Response time measurements
- Concurrent load testing
- Memory usage monitoring
- Error recovery testing
- Streaming performance testing
- Statistical analysis of performance metrics

**Usage**:
```bash
python performance_test.py
```

### 3. `integration_test.py` - Integration Tests
**Purpose**: End-to-end workflow testing and complete user scenario validation.

**Tests Include**:
- Leave application workflow (balance check → policy inquiry → application)
- Payroll inquiry workflow (salary → payslip → tax documents → deductions)
- Policy inquiry workflow (working hours → dress code → leave carry forward → sick leave)
- Escalation workflow (complex issue → human support → ticket creation)
- Mixed workflow testing
- Context persistence across interactions
- Error handling in workflows
- Agent delegation validation

**Usage**:
```bash
python integration_test.py
```

### 4. `run_tests.py` - Test Runner
**Purpose**: Unified test runner that can execute all test suites or specific types.

**Features**:
- Run all tests or specific test types
- Server status checking
- Command-line argument support
- Comprehensive reporting

**Usage**:
```bash
# Run all tests
python run_tests.py

# Run specific test type
python run_tests.py --type functional
python run_tests.py --type performance
python run_tests.py --type integration

# Check server status before running tests
python run_tests.py --check-server

# Verbose output
python run_tests.py --verbose
```

## Prerequisites

1. **Server Running**: Ensure the ESS Agents API server is running on `http://127.0.0.1:8000`
   ```bash
   cd backend
   python main.py
   ```

2. **Dependencies**: Install required packages
   ```bash
   pip install requests matplotlib numpy
   ```

## Test Categories

### Functional Tests
- **Basic Operations**: Simple query/response validation
- **Agent Routing**: Verify queries are routed to correct agents
- **Error Handling**: Test system behavior with invalid inputs
- **State Management**: Validate session state persistence
- **API Endpoints**: Test all available endpoints

### Performance Tests
- **Response Times**: Measure and analyze response time statistics
- **Concurrent Load**: Test system under multiple simultaneous requests
- **Memory Usage**: Monitor memory consumption during extended use
- **Error Recovery**: Test system recovery after errors
- **Streaming Performance**: Validate real-time streaming functionality

### Integration Tests
- **Complete Workflows**: Test end-to-end user scenarios
- **Agent Coordination**: Verify proper agent delegation and handoffs
- **Context Persistence**: Ensure user context is maintained across interactions
- **Error Scenarios**: Test error handling in complex workflows
- **Mixed Operations**: Test various query types in sequence

## Expected Test Results

### Functional Tests
- All basic queries should return 200 status codes
- Agent delegation should work correctly
- State should persist across requests
- Error cases should be handled gracefully

### Performance Tests
- Average response time: < 5 seconds
- Concurrent requests should be handled without errors
- Memory usage should remain stable
- Streaming should work without timeouts

### Integration Tests
- Complete workflows should execute successfully
- Context should be maintained throughout workflows
- Agent handoffs should be smooth
- Error recovery should work in complex scenarios

## Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   Error: Connection refused
   Solution: Start the server with `python main.py`
   ```

2. **Import Errors**
   ```
   Error: No module named 'requests'
   Solution: Install dependencies with `pip install requests`
   ```

3. **Timeout Errors**
   ```
   Error: Request timeout
   Solution: Check server performance or increase timeout values
   ```

4. **State Issues**
   ```
   Error: Session not found
   Solution: Restart the server to create a new session
   ```

### Debug Mode

To run tests with more detailed output:
```bash
python run_tests.py --verbose
```

### Individual Test Execution

To run specific test functions:
```python
# In Python console
from test import ESSAgentTests
tester = ESSAgentTests()
tester.test_basic_query()
```

## Test Data

The tests use realistic queries that employees might ask:
- Leave-related: "What is my leave balance?", "How do I apply for leave?"
- Payroll-related: "When will I get my salary?", "How can I download my payslip?"
- Policy-related: "What are the working hours?", "What is the dress code policy?"
- Support-related: "I need to speak to HR", "Create a support ticket"

## Continuous Integration

These tests can be integrated into CI/CD pipelines:
```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd backend
    python run_tests.py --check-server --type all
```

## Contributing

When adding new features to the ESS Agents system:

1. **Add Functional Tests**: Test the new functionality in `test.py`
2. **Add Performance Tests**: If applicable, add performance tests in `performance_test.py`
3. **Add Integration Tests**: Test complete workflows in `integration_test.py`
4. **Update Documentation**: Update this README with new test descriptions

## Test Maintenance

- **Regular Updates**: Update tests when API changes
- **Performance Baselines**: Monitor and update performance expectations
- **Test Data**: Keep test queries relevant to actual use cases
- **Dependencies**: Keep test dependencies up to date 