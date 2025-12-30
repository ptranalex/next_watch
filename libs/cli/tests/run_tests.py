#!/usr/bin/env python3
"""Simple test runner for CLI Framework tests.

This script runs tests without requiring pytest, making it easier to verify
basic functionality during development.
"""

import sys
import traceback
from collections.abc import Callable


def run_test_function(test_func: Callable[[], None], test_name: str) -> tuple[bool, str]:
    """Run a single test function and return result.

    Args:
        test_func: Test function to run
        test_name: Name of the test for reporting

    Returns:
        Tuple of (success, error_message)
    """
    try:
        test_func()
        return True, ""
    except Exception as e:
        error_msg = f"{test_name}: {str(e)}\n{traceback.format_exc()}"
        return False, error_msg


def run_tests() -> int:
    """Run all CLI framework tests.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("🧪 Running CLI Framework Tests")
    print("=" * 50)

    # Import test classes
    try:
        from tests.test_base import (
            create_sample_health_results,
            create_test_service_registry,
        )
        from tests.test_service_registry import (
            TestServiceConfig,
            TestServiceRegistry,
            TestServiceRegistryIntegration,
        )
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return 1

    # Collect all test methods
    test_classes = [
        TestServiceConfig,
        TestServiceRegistry,
        TestServiceRegistryIntegration,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests: list[str] = []

    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)

        # Create test instance
        test_instance = test_class()

        # Find all test methods
        test_methods = [method for method in dir(test_instance) if method.startswith("test_")]

        for method_name in test_methods:
            total_tests += 1

            # Set up the test
            if hasattr(test_instance, "setup_method"):
                test_instance.setup_method()

            # Run the test
            test_method = getattr(test_instance, method_name)
            success, error_msg = run_test_function(
                test_method, f"{test_class.__name__}.{method_name}"
            )

            if success:
                passed_tests += 1
                print(f"  ✅ {method_name}")
            else:
                failed_tests.append(error_msg)
                print(f"  ❌ {method_name}")

            # Tear down the test
            if hasattr(test_instance, "teardown_method"):
                try:
                    test_instance.teardown_method()
                except Exception as e:
                    print(f"  ⚠️  Teardown warning for {method_name}: {e}")

    # Test utility functions
    print("\n📋 Running Utility Function Tests")
    print("-" * 40)

    def test_sample_health_results() -> None:
        """Test sample health results factory."""
        results = create_sample_health_results()
        assert "backend-api" in results
        assert "auth-api" in results
        assert "redis" in results
        assert results["backend-api"].is_healthy is True
        assert results["redis"].is_healthy is False

    def test_test_service_registry() -> None:
        """Test service registry factory."""
        registry = create_test_service_registry()
        assert len(registry) == 2
        assert "backend-api" in registry
        assert "redis" in registry

    utility_tests = [
        (test_sample_health_results, "test_sample_health_results"),
        (test_test_service_registry, "test_test_service_registry"),
    ]

    for test_func, test_name in utility_tests:
        total_tests += 1
        success, error_msg = run_test_function(test_func, test_name)

        if success:
            passed_tests += 1
            print(f"  ✅ {test_name}")
        else:
            failed_tests.append(error_msg)
            print(f"  ❌ {test_name}")

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {len(failed_tests)} ❌")

    if failed_tests:
        print("\n💥 Failed Test Details:")
        for i, error in enumerate(failed_tests, 1):
            print(f"\n{i}. {error}")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
