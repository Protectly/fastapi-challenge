#!/usr/bin/env python3
"""
Test runner for the FastAPI interview project.
This script runs tests and shows you what's broken vs what works.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Test took too long")
        return False
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return False


def main():
    print("🚀 FastAPI Interview Project - Test Results")
    print("\nThis will show you what's broken and needs to be fixed!\n")

    # Check if we can import the app (this will fail immediately with current bugs)
    print("Step 1: Checking if the application can be imported...")
    can_import = run_command(
        "uv run python -c \"import app.main; print('✅ App imported successfully')\"",
        "Testing Basic App Import",
    )

    if not can_import:
        print("\n🔥 CRITICAL: The app cannot even be imported!")
        print(
            "   This means there are syntax errors, import errors, or database issues."
        )
        print("   Fix these first before running tests.")
        print("\n💡 Common issues to check:")
        print("   - Missing dependencies (check pyproject.toml)")
        print("   - Import errors in routers")
        print("   - Database connection issues")
        print("   - Syntax errors (unclosed strings, etc.)")

        # Still try to run a simple test to see what happens
        print("\nLet's try running tests anyway to see what errors we get...")

    # Try to run tests
    test_commands = [
        (
            "uv run python -m pytest app/tests/test_main.py -v",
            "Testing Main App Functionality",
        ),
        (
            "uv run python -m pytest app/tests/test_auth.py::TestUserRegistration::test_register_user_success -v",
            "Testing User Registration",
        ),
        (
            "uv run python -m pytest app/tests/test_tasks.py::TestTaskCreation::test_create_task_success -v",
            "Testing Task Creation",
        ),
    ]

    all_passed = True
    for cmd, desc in test_commands:
        passed = run_command(cmd, desc)
        if not passed:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed and can_import:
        print("🎉 ALL TESTS PASSED! Great job fixing the bugs!")
    else:
        print("📝 SUMMARY OF ISSUES TO FIX:")
        print("   1. Start by getting the app to import successfully")
        print("   2. Fix any syntax errors or missing dependencies")
        print("   3. Run individual test files to see specific failures")
        print("   4. Use 'uv run python -m pytest -v' for detailed test output")
        print("\n💡 Helpful commands:")
        print("   uv run python -m pytest app/tests/test_auth.py -v")
        print("   uv run python -m pytest app/tests/test_tasks.py -v")
        print("   uv run python -m pytest app/tests/test_main.py -v")

    print("=" * 60)


if __name__ == "__main__":
    main()
