## Testing

AWS Auto Inventory uses pytest for testing. To run the tests:

1. Install the test dependencies:

```bash
pip install -r test_requirements.txt
```

2. Run the tests:

```bash
pytest
```

3. Run tests with coverage:

```bash
pytest --cov=. tests/
```

### Test Structure

The tests are organized as follows:

- **Unit Tests**: Test individual components in isolation
  - `test_api_calls.py`: Tests for API call handling and retry logic
  - `test_organization.py`: Tests for organization account discovery
  - `test_role_assumption.py`: Tests for role assumption functionality
  
- **Integration Tests**: Test components working together
  - `test_organization_scanner.py`: Tests for the organization scanning workflow
  - `test_service_scanning.py`: Tests for service scanning functionality

### Mocking AWS Services

The tests use the `moto` library to mock AWS services, allowing tests to run without actual AWS credentials or resources.