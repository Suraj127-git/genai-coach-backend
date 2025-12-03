#!/usr/bin/env python3
"""
Test runner script for Railway API endpoint testing.

This script provides various options for running tests against the
Railway production API endpoint.
"""
import os
import sys
import argparse
import subprocess
from typing import List, Optional


# Railway API endpoint
DEFAULT_API_URL = "https://genai-coach-backend-production.up.railway.app"


def run_pytest(args: List[str]) -> int:
    """
    Run pytest with the given arguments.

    Args:
        args: List of pytest arguments

    Returns:
        Exit code from pytest
    """
    cmd = ["pytest"] + args
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run API tests against Railway endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py

  # Run only authentication tests
  python run_tests.py --auth

  # Run smoke tests only
  python run_tests.py --smoke

  # Run with verbose output
  python run_tests.py -v

  # Run specific test file
  python run_tests.py --file test_auth.py

  # Run tests in parallel (fast)
  python run_tests.py --parallel

  # Generate HTML report
  python run_tests.py --html
        """
    )

    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"API base URL (default: {DEFAULT_API_URL})",
    )

    # Test selection
    parser.add_argument("--auth", action="store_true", help="Run only authentication tests")
    parser.add_argument("--sessions", action="store_true", help="Run only session tests")
    parser.add_argument("--upload", action="store_true", help="Run only upload tests")
    parser.add_argument("--ai", action="store_true", help="Run only AI chat tests")
    parser.add_argument("--smoke", action="store_true", help="Run only smoke tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--file", help="Run specific test file")

    # Output options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet output")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")

    # Performance options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("-n", "--workers", type=int, help="Number of parallel workers")

    # Other options
    parser.add_argument("--failfast", action="store_true", help="Stop on first failure")
    parser.add_argument("--pdb", action="store_true", help="Drop into debugger on failure")

    args = parser.parse_args()

    # Set API URL environment variable
    os.environ["API_URL"] = args.api_url

    # Build pytest arguments
    pytest_args = []

    # Test selection
    if args.auth:
        pytest_args.extend(["-m", "auth"])
    elif args.sessions:
        pytest_args.extend(["-m", "sessions"])
    elif args.upload:
        pytest_args.extend(["-m", "upload"])
    elif args.ai:
        pytest_args.extend(["-m", "ai"])
    elif args.smoke:
        pytest_args.extend(["-m", "smoke"])
    elif args.integration:
        pytest_args.extend(["-m", "integration"])
    elif args.file:
        pytest_args.append(args.file)

    # Verbosity
    if args.verbose:
        pytest_args.append("-vv")
    elif args.quiet:
        pytest_args.append("-q")

    # Reports
    if args.html:
        pytest_args.extend(["--html=test_report.html", "--self-contained-html"])
        print("HTML report will be generated at: test_report.html")
    if args.json:
        pytest_args.extend(["--json-report", "--json-report-file=test_report.json"])
        print("JSON report will be generated at: test_report.json")

    # Parallel execution
    if args.parallel or args.workers:
        workers = args.workers or "auto"
        pytest_args.extend(["-n", str(workers)])

    # Other options
    if args.failfast:
        pytest_args.append("-x")
    if args.pdb:
        pytest_args.append("--pdb")

    # Run the tests
    print(f"Testing API endpoint: {args.api_url}")
    print("=" * 80)

    exit_code = run_pytest(pytest_args)

    print("=" * 80)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
