"""Test runner configuration for vSPACE tests."""

import pytest
import sys
import os

# Add package path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)


def run_all_tests():
    """Run all vSPACE tests."""
    test_dir = os.path.dirname(__file__)

    return pytest.main(
        [
            test_dir,
            "-v",
            "--tb=short",
            "-p",
            "no:warnings",
        ]
    )


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
