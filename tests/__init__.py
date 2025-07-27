# Tests configuration and utilities
import os
import sys

# Add the package root to Python path for testing
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# Test configuration
TEST_TIMEOUT = 30  # seconds
BENCHMARK_ITERATIONS = {'small': 1000, 'medium': 10000, 'large': 100000}


def ensure_extensions_built():
    """Ensure C/C++ extensions are built before running tests."""
    try:
        # Try importing all extensions to verify they're built
        from ax_utils.ax_queue import AXQueue
        from ax_utils.props_to_tree import props_to_tree
        from ax_utils.simple_deepcopy import deepcopy
        from ax_utils.unicode_utils import is_utf8

        return True
    except ImportError as e:
        print(f'⚠️  Extension not built: {e}')
        print("Run 'just build' or 'python setup.py build_ext --inplace' first")
        return False


def print_test_header(test_name):
    """Print a formatted test header."""
    print(f'\n{"=" * 60}')
    print(f'🧪 {test_name}')
    print(f'{"=" * 60}')


def print_test_result(test_name, passed, details=None):
    """Print formatted test results."""
    status = '✅ PASSED' if passed else '❌ FAILED'
    print(f'{status}: {test_name}')
    if details:
        print(f'   {details}')
