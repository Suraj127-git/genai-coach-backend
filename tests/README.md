# API Testing Suite

Comprehensive pytest test suite for the GenAI Coach Backend API deployed on Railway.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd genai-coach-backend/tests
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Simple run
pytest

# Or use the test runner script
python run_tests.py
```

### 3. Run Specific Test Categories

```bash
# Authentication tests only
python run_tests.py --auth

# Session management tests only
python run_tests.py --sessions

# Upload tests only
python run_tests.py --upload

# AI chat tests only
python run_tests.py --ai

# Smoke tests (quick essential tests)
python run_tests.py --smoke
```

## 📋 Test Coverage

### Test Files

| File | Description | Test Count |
|------|-------------|------------|
| `test_health.py` | API health and connectivity | 5 tests |
| `test_auth.py` | Authentication endpoints | 30+ tests |
| `test_sessions.py` | Interview session management | 25+ tests |
| `test_upload.py` | File upload (S3 presigned URLs) | 20+ tests |
| `test_ai.py` | AI chat functionality | 20+ tests |

### API Endpoints Tested

#### Authentication (`/auth`)
- ✅ `POST /auth/register` - User registration
- ✅ `POST /auth/login` - User login
- ✅ `POST /auth/refresh` - Token refresh
- ✅ `POST /auth/logout` - User logout
- ✅ `GET /auth/me` - Get current user profile
- ✅ `PUT /auth/me` - Update user profile

#### Sessions (`/sessions`)
- ✅ `POST /sessions` - Create interview session
- ✅ `GET /sessions` - List user sessions
- ✅ `GET /sessions/{id}` - Get specific session
- ✅ `GET /sessions/{id}/feedback` - Get session feedback
- ✅ `POST /sessions/{id}/complete` - Complete session

#### Upload (`/upload`)
- ✅ `POST /upload/s3-presign` - Generate presigned URL
- ✅ `POST /upload/confirm` - Confirm upload completion

#### AI (`/ai`)
- ✅ `POST /ai/chat` - Chat with AI assistant

## 🎯 Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.smoke` - Essential smoke tests (quick validation)
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.sessions` - Session management tests
- `@pytest.mark.upload` - File upload tests
- `@pytest.mark.ai` - AI service tests
- `@pytest.mark.integration` - End-to-end integration tests

## 🔧 Usage Examples

### Run Tests with Verbosity

```bash
# Verbose output
python run_tests.py -v

# Very verbose output
pytest -vv

# Quiet mode
python run_tests.py -q
```

### Run Specific Test File

```bash
# Using pytest directly
pytest test_auth.py

# Using test runner
python run_tests.py --file test_auth.py
```

### Run Specific Test

```bash
# Run single test by name
pytest test_auth.py::TestAuthRegistration::test_register_success

# Run all tests in a class
pytest test_auth.py::TestAuthRegistration
```

### Stop on First Failure

```bash
python run_tests.py --failfast

# Or with pytest
pytest -x
```

### Generate Test Report

```bash
# HTML report (requires pytest-html)
pip install pytest-html
python run_tests.py --html

# View report
open test_report.html
```

### Run Tests Against Custom API URL

```bash
# Set custom API URL
export API_URL=https://your-custom-url.railway.app
pytest

# Or pass directly to test runner
python run_tests.py --api-url https://your-custom-url.railway.app
```

## 🧪 Test Structure

### Fixtures (conftest.py)

The test suite uses pytest fixtures for common setup:

- `client` - Async HTTP client for API requests
- `base_url` - API base URL (Railway endpoint)
- `test_user` - Auto-created test user with credentials
- `auth_headers` - Authentication headers with valid token
- `test_session` - Pre-created interview session
- `random_email`, `random_password`, `random_name` - Random test data generators

### Example Test Usage

```python
async def test_example(client, auth_headers):
    """Example test using fixtures."""
    response = await client.get("/sessions", headers=auth_headers)
    assert response.status_code == 200
```

## 📊 Test Scenarios Covered

### Authentication Tests
- ✅ Successful registration with valid data
- ✅ Duplicate email validation
- ✅ Invalid email format handling
- ✅ Password length validation
- ✅ Successful login with credentials
- ✅ Login with wrong password
- ✅ Login with non-existent user
- ✅ Token refresh mechanism
- ✅ Invalid token handling
- ✅ Profile retrieval and updates
- ✅ Password change workflow
- ✅ Logout functionality

### Session Tests
- ✅ Create session with valid data
- ✅ List user sessions with statistics
- ✅ Retrieve specific session
- ✅ Session not found handling
- ✅ Complete session workflow
- ✅ Generate session feedback
- ✅ User isolation (can't access others' sessions)
- ✅ Full session lifecycle integration

### Upload Tests
- ✅ Generate presigned URL for various formats (m4a, mp3, wav, mp4)
- ✅ Unique key generation
- ✅ Upload confirmation
- ✅ Invalid S3 key handling
- ✅ Missing parameters validation
- ✅ Concurrent presign requests

### AI Chat Tests
- ✅ Successful chat interaction
- ✅ Interview-related questions
- ✅ Technical questions
- ✅ Empty message handling
- ✅ Long message handling
- ✅ Special characters support
- ✅ Code snippets in messages
- ✅ Multiple sequential messages
- ✅ Various interview topics

## 🐛 Debugging Failed Tests

### View Full Error Details

```bash
pytest -vv --tb=long
```

### Drop into Debugger on Failure

```bash
python run_tests.py --pdb
```

### Run Single Failing Test

```bash
pytest test_auth.py::TestAuthLogin::test_login_wrong_password -vv
```

### Check API Response

Tests are designed to show response content on failure:

```python
assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
```

## 🔍 Common Issues and Solutions

### Issue: All tests failing with connection error

**Solution:** Verify Railway API is running:
```bash
curl https://genai-coach-backend-production.up.railway.app/
```

### Issue: Authentication tests failing

**Possible causes:**
- Database issues on Railway
- Token expiration settings
- Password hashing configuration

**Debug:**
```bash
pytest test_auth.py::TestAuthRegistration::test_register_success -vv
```

### Issue: Random test failures

**Cause:** Tests create real data on the API
**Solution:** Each test uses unique random emails via Faker

### Issue: Upload tests failing

**Cause:** Upload tests may fail if S3 configuration is missing
**Expected:** Some upload confirm tests may fail without actual S3 upload

### Issue: AI tests failing

**Cause:** AI service (OpenAI) might be unavailable or rate-limited
**Solution:** Check backend logs on Railway for API errors

## 📈 Performance Testing

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with auto-detected workers
pytest -n auto

# Or specify worker count
pytest -n 4
```

### Measure Test Duration

```bash
pytest --durations=10  # Show 10 slowest tests
```

## 🎓 Best Practices

1. **Always test against Railway endpoint** - These tests are designed for production API
2. **Use unique test data** - Fixtures generate random emails to avoid conflicts
3. **Check response status AND content** - Don't just check status codes
4. **Clean up is handled automatically** - Tests create isolated data
5. **Run smoke tests first** - Quick validation before full test suite

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd genai-coach-backend/tests
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd genai-coach-backend/tests
          pytest --html=report.html
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: genai-coach-backend/tests/report.html
```

## 📝 Writing New Tests

### Template for New Test

```python
import pytest
import httpx
from typing import Dict, Any

@pytest.mark.your_category
class TestYourFeature:
    """Test your feature description."""

    async def test_your_scenario(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test scenario description."""
        # Arrange
        test_data = {"key": "value"}

        # Act
        response = await client.post(
            "/your-endpoint",
            json=test_data,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

## 📞 Support

For issues or questions:
- Check Railway logs: `railway logs`
- Review API docs: Check `ARCHITECTURE.md` in backend repo
- Run individual tests with `-vv` flag for details

## 🎉 Summary

This test suite provides comprehensive coverage of the GenAI Coach Backend API:

- **100+ test cases** across all major endpoints
- **Automated fixtures** for easy test writing
- **Multiple test categories** for targeted testing
- **Integration tests** for end-to-end workflows
- **Railway-ready** - Designed for production API testing

Happy Testing! 🚀
