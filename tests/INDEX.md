# API Test Suite - Complete Index

## 🎯 Quick Navigation

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes | 5 min |
| [README.md](README.md) | Complete testing guide | 15 min |
| [TEST_SUMMARY.md](TEST_SUMMARY.md) | Test coverage overview | 10 min |
| [INDEX.md](INDEX.md) | This file - navigation hub | 2 min |

## 📁 Project Structure

```
tests/
├── 📖 Documentation
│   ├── INDEX.md              ← You are here
│   ├── QUICKSTART.md         ← Start here if new
│   ├── README.md             ← Comprehensive guide
│   └── TEST_SUMMARY.md       ← Coverage details
│
├── ⚙️ Configuration
│   ├── pytest.ini            ← Pytest settings
│   ├── conftest.py           ← Shared fixtures
│   └── requirements-test.txt ← Dependencies
│
├── 🧪 Test Files (78 tests, ~1,400 LOC)
│   ├── test_health.py        ← API health (5 tests)
│   ├── test_auth.py          ← Authentication (30+ tests)
│   ├── test_sessions.py      ← Sessions (25+ tests)
│   ├── test_upload.py        ← Uploads (20+ tests)
│   └── test_ai.py            ← AI chat (20+ tests)
│
└── 🚀 Runner Scripts
    ├── setup_and_test.sh     ← One-command setup
    ├── run_tests.sh          ← Quick test runner
    └── run_tests.py          ← Advanced test runner
```

## 🚀 Getting Started

### First Time Setup (1 minute)

```bash
# Navigate to tests directory
cd genai-coach-backend/tests

# Run setup and smoke tests
./setup_and_test.sh
```

This will:
1. ✅ Check Python version
2. ✅ Install dependencies
3. ✅ Verify API health
4. ✅ Run smoke tests
5. ✅ Show next steps

### Daily Usage

```bash
# Quick smoke test before starting work
./run_tests.sh --smoke

# Test specific feature you're working on
./run_tests.sh --auth      # Authentication
./run_tests.sh --sessions  # Sessions
./run_tests.sh --upload    # Uploads
./run_tests.sh --ai        # AI chat

# Full test suite
./run_tests.sh
```

## 📚 Documentation Guide

### For First-Time Users
1. Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Run `./setup_and_test.sh`
3. Explore test files
4. Read [README.md](README.md) when ready

### For Developers
1. Review [TEST_SUMMARY.md](TEST_SUMMARY.md) for coverage
2. Check `conftest.py` for available fixtures
3. Use test files as examples
4. Refer to [README.md](README.md) for advanced usage

### For DevOps/CI
1. Check [README.md](README.md) CI/CD section
2. Use `run_tests.py` for advanced options
3. Set `API_URL` environment variable
4. Review exit codes for pipeline integration

## 🎓 Learning Path

### Level 1: Beginner
- [ ] Read QUICKSTART.md
- [ ] Install dependencies
- [ ] Run smoke tests
- [ ] Run single test file

### Level 2: Intermediate
- [ ] Understand fixtures (conftest.py)
- [ ] Run tests by marker
- [ ] Use verbose mode
- [ ] Read test file contents

### Level 3: Advanced
- [ ] Write custom tests
- [ ] Use Python runner with options
- [ ] Generate reports
- [ ] Integrate with CI/CD

## 📊 Test Statistics

```
Total Files:       15 files
Total Lines:       3,050 lines
Test Files:        5 files
Test Functions:    78+ tests
Coverage:          100% of API endpoints
Execution Time:    3-5 minutes (all), 10-30s (smoke)
```

## 🔗 API Endpoint

```
Production: https://genai-coach-backend-production.up.railway.app
```

## 🛠️ Common Commands Cheat Sheet

```bash
# Setup
pip install -r requirements-test.txt

# Quick tests
./run_tests.sh --smoke              # Fastest
./run_tests.sh --auth               # Auth only
./run_tests.sh                      # All tests

# With pytest
pytest -m smoke                     # Smoke tests
pytest test_auth.py                 # Single file
pytest -v                           # Verbose
pytest -x                           # Stop on first failure
pytest -k "login"                   # Match pattern

# Advanced
python run_tests.py --help          # See all options
pytest --html=report.html           # Generate report
pytest -vv --tb=long                # Debug mode
```

## 📦 Files Overview

### Documentation (4 files)
- **INDEX.md** - Navigation hub (this file)
- **QUICKSTART.md** - 5-minute quick start
- **README.md** - Complete guide with examples
- **TEST_SUMMARY.md** - Coverage and statistics

### Configuration (3 files)
- **pytest.ini** - Pytest configuration
- **conftest.py** - Shared fixtures and utilities
- **requirements-test.txt** - Python dependencies

### Tests (5 files, 78+ tests)
- **test_health.py** - Basic connectivity (5 tests)
- **test_auth.py** - Authentication flows (30+ tests)
- **test_sessions.py** - Session management (25+ tests)
- **test_upload.py** - File uploads (20+ tests)
- **test_ai.py** - AI chat service (20+ tests)

### Runners (3 files)
- **setup_and_test.sh** - One-command setup
- **run_tests.sh** - Quick bash runner
- **run_tests.py** - Advanced Python runner

## 🎯 Use Cases

### "I want to verify the API is working"
→ Run: `./run_tests.sh --smoke`

### "I'm working on authentication"
→ Run: `./run_tests.sh --auth`

### "I need to test everything before deployment"
→ Run: `./run_tests.sh`

### "I want to see what failed"
→ Run: `pytest -vv --tb=short`

### "I need a test report"
→ Run: `python run_tests.py --html`

### "I'm new to this project"
→ Read: `QUICKSTART.md` then run `./setup_and_test.sh`

## ✅ Next Steps

1. **New User?** Start with [QUICKSTART.md](QUICKSTART.md)
2. **Need Details?** See [README.md](README.md)
3. **Want Coverage Info?** Check [TEST_SUMMARY.md](TEST_SUMMARY.md)
4. **Ready to Test?** Run `./setup_and_test.sh`

## 💡 Tips

- Use `--smoke` flag for quick validation
- Run tests before starting frontend work
- Check API health if tests fail: `curl https://genai-coach-backend-production.up.railway.app/`
- Use `-vv` for detailed output
- Tests generate unique data, safe to run multiple times

## 🎉 You're All Set!

The test suite is comprehensive and ready to use. Choose your path:

- **Quick Start**: `./setup_and_test.sh`
- **Learn More**: Read [QUICKSTART.md](QUICKSTART.md)
- **Deep Dive**: Read [README.md](README.md)
- **See Coverage**: Read [TEST_SUMMARY.md](TEST_SUMMARY.md)

Happy Testing! 🚀
