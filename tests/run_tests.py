#!/usr/bin/env python3
"""
Test runner script for the data ingestion and preprocessing pipeline.

This script provides a convenient way to run all tests with different configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """
    Run tests with the specified configuration.
    
    Args:
        test_type: Type of tests to run ("all", "unit", "integration", "performance")
        verbose: Whether to run tests in verbose mode
        coverage: Whether to generate coverage report
        parallel: Whether to run tests in parallel
    """
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/")
    
    # Add test type filter
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        cmd.extend(["-m", "slow"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage flag
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add parallel flag
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add other useful flags
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings",  # Disable warnings for cleaner output
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1


def run_specific_test(test_file, verbose=False):
    """
    Run a specific test file.
    
    Args:
        test_file: Path to the test file
        verbose: Whether to run tests in verbose mode
    """
    cmd = ["python", "-m", "pytest", test_file]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ Test passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Test failed!")
        return e.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the data ingestion and preprocessing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --type unit        # Run only unit tests
  python run_tests.py --type integration # Run only integration tests
  python run_tests.py --type performance # Run only performance tests
  python run_tests.py --type fast        # Run only fast tests (exclude performance)
  python run_tests.py --verbose          # Run tests in verbose mode
  python run_tests.py --coverage         # Run tests with coverage report
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --file tests/test_validators.py  # Run specific test file
        """
    )
    
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "performance", "fast"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Run a specific test file"
    )
    
    args = parser.parse_args()
    
    # Check if tests directory exists
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        print("Please run this script from the project root directory.")
        return 1
    
    # Run specific test file if specified
    if args.file:
        test_file = Path(args.file)
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return 1
        return run_specific_test(str(test_file), args.verbose)
    
    # Run tests based on type
    return run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )


if __name__ == "__main__":
    sys.exit(main())
