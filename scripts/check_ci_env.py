#!/usr/bin/env python3
"""
GitHub Actions status checker for ax_utils

This script helps verify that your local environment matches
the CI environment requirements.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f'🔍 {description}...')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'  ✅ {description} - PASSED')
            return True
        else:
            print(f'  ❌ {description} - FAILED')
            print(f'     Error: {result.stderr.strip()}')
            return False
    except Exception as e:
        print(f'  ❌ {description} - ERROR: {e}')
        return False


def check_python_version():
    """Check if Python version is supported."""
    version = sys.version_info
    supported = version >= (3, 9)
    status = '✅' if supported else '❌'
    print(f'{status} Python {version.major}.{version.minor} '
          f'(supported: 3.9+)')
    return supported


def main():
    """Main CI environment check."""
    print('🚀 ax_utils CI Environment Check')
    print('=' * 40)
    
    checks = []
    
    # Python version check
    checks.append(check_python_version())
    
    # Tool availability checks
    checks.append(run_command('uv --version', 'UV package manager'))
    checks.append(run_command('python --version', 'Python availability'))
    
    # Project setup checks
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / 'pyproject.toml'
    
    if pyproject_path.exists():
        print('  ✅ pyproject.toml found')
        checks.append(True)
    else:
        print('  ❌ pyproject.toml not found')
        checks.append(False)
    
    # Try to install dependencies
    checks.append(run_command('uv sync --dev', 'Dependency installation'))
    
    # Try to build extensions
    checks.append(run_command(
        'uv run python setup.py build_ext --inplace', 
        'C++ extension building'
    ))
    
    # Code quality checks
    checks.append(run_command(
        'uv run ruff check ax_utils/ tests/', 
        'Ruff linting'
    ))
    checks.append(run_command(
        'uv run ruff format --check ax_utils/ tests/', 
        'Ruff formatting'
    ))
    checks.append(run_command(
        'uv run mypy ax_utils/ --ignore-missing-imports', 
        'Type checking'
    ))
    
    # Import tests
    import_test = """
from ax_utils.ax_queue import AXQueue
from ax_utils.ax_tree import AXTree 
from ax_utils.props_to_tree import props_to_tree
from ax_utils.unicode_utils import is_utf8
print('All imports successful')
"""
    
    checks.append(run_command(
        f'uv run python -c "{import_test.strip()}"',
        'Module imports'
    ))
    
    # Quick functionality test
    checks.append(run_command(
        'uv run python scripts/quick_test.py',
        'Quick functionality test'
    ))
    
    # Summary
    print('\n' + '=' * 40)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f'🎉 All checks passed! ({passed}/{total})')
        print('✅ Your environment is ready for CI')
        return 0
    else:
        print(f'⚠️  Some checks failed ({passed}/{total})')
        print('❌ Please fix the issues above before pushing')
        return 1


if __name__ == '__main__':
    sys.exit(main())
