# Quick Start Guide - API Testing

Get started with testing the Railway API in under 5 minutes!

## Prerequisites

- Python 3.8+
- pip

## Step 1: Install Dependencies

```bash
cd genai-coach-backend/tests
pip install -r requirements-test.txt
```

This installs:
- pytest (test framework)
- pytest-asyncio (async test support)
- httpx (HTTP client)
- faker (test data generation)

## Step 2: Run Your First Test

### Option A: Using the Shell Script (Recommended)

```bash
# Run smoke tests (fastest)
./run_tests.sh --smoke

# Run all tests
./run_tests.sh
```

### Option B: Using Python Script

```bash
# Run smoke tests
python run_tests.py --smoke

# Run all tests
python run_tests.py
```

### Option C: Using pytest Directly

```bash
# Run smoke tests
pytest -m smoke

# Run all tests
pytest
```

## Step 3: Understand the Results

### ✅ Successful Test Output

```
test_health.py::TestAPIHealth::test_api_reachable PASSED
test_auth.py::TestAuthRegistration::test_register_success PASSED
```

### ❌ Failed Test Output

```
test_auth.py::TestAuthLogin::test_login_wrong_password FAILED
AssertionError: Expected 401, got 500: {"detail": "Internal server error"}
```

## Common Commands

### Test Specific Features

```bash
# Test authentication only
./run_tests.sh --auth

# Test sessions only
./run_tests.sh --sessions

# Test uploads only
./run_tests.sh --upload

# Test AI chat only
./run_tests.sh --ai
```

### Verbose Output

```bash
# See detailed output
pytest -vv

# Or with shell script
./run_tests.sh -v
```

### Run Single Test File

```bash
pytest test_auth.py
```

### Run Single Test

```bash
pytest test_auth.py::TestAuthRegistration::test_register_success -v
```

## What Gets Tested?

| Endpoint | What's Tested |
|----------|---------------|
| `POST /auth/register` | User registration with validation |
| `POST /auth/login` | Login with credentials |
| `POST /auth/refresh` | Token refresh mechanism |
| `GET /auth/me` | Profile retrieval |
| `PUT /auth/me` | Profile updates |
| `POST /sessions` | Create interview sessions |
| `GET /sessions` | List sessions |
| `GET /sessions/{id}/feedback` | Get AI feedback |
| `POST /upload/s3-presign` | Generate upload URLs |
| `POST /ai/chat` | Chat with AI |

## Test Data

Tests automatically generate unique test data using Faker:
- Random emails: `test123@example.com`
- Random names: `John Doe`
- Random passwords: Strong passwords with special characters

Each test run creates fresh data, so tests don't conflict with each other.

## Troubleshooting

### Problem: "Module not found" error

**Solution:**
```bash
pip install -r requirements-test.txt
```

### Problem: "Connection refused" error

**Solution:** Check if Railway API is up:
```bash
curl https://genai-coach-backend-production.up.railway.app/
```

### Problem: Tests are slow

**Solution:** Run smoke tests only:
```bash
./run_tests.sh --smoke
```

### Problem: Want to see what's happening

**Solution:** Use verbose mode:
```bash
pytest -vv test_auth.py
```

## Next Steps

1. **Read the full README.md** for advanced usage
2. **Check test_*.py files** to see what's tested
3. **Run integration tests** with `pytest -m integration`
4. **Write your own tests** using the provided fixtures

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./run_tests.sh --smoke` | Quick smoke test (5-10 tests) |
| `./run_tests.sh --auth` | Authentication tests (~30 tests) |
| `./run_tests.sh` | All tests (~100+ tests) |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest test_auth.py` | Test single file |

## Expected Test Duration

- **Smoke tests**: 10-30 seconds
- **Single category** (e.g., auth): 1-2 minutes
- **All tests**: 3-5 minutes

Happy Testing! 🎉

---

**Need Help?**
- See [README.md](README.md) for detailed documentation
- Check [conftest.py](conftest.py) for available fixtures
- Review test files for examples
