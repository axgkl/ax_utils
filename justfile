# ax_utils development tasks
# Requires: just (https://github.com/casey/just)
# Install: brew install just

# Default recipe - show help
default:
    @just --list

# 🔧 Check CI environment compatibility
check-ci:
    @echo "🔍 Checking CI environment compatibility..."
    uv run python scripts/check_ci_env.py

# 🧹 Clean all build artifacts and caches
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.so" -delete 2>/dev/null || true
    @echo "✅ Clean complete"

# 🔧 Install development dependencies
install-dev:
    @echo "🔧 Installing development dependencies..."
    uv add --dev pytest pytest-cov pytest-benchmark pytest-xdist
    uv add --dev ruff mypy
    @echo "✅ Development dependencies installed"

# 🏗️ Build C/C++ extensions in-place for development
build:
    @echo "🏗️ Building C/C++ extensions..."
    uv run python setup.py build_ext --inplace
    @echo "✅ Extensions built successfully"

# 📦 Build distribution packages (source + wheel)
dist: clean
    @echo "📦 Building distribution packages..."
    uv build
    @echo "✅ Distribution packages built:"
    @ls -la dist/

# 🧪 Run all tests
test: build
    @echo "🧪 Running test suite..."
    uv run python -m pytest tests/ -v --tb=short

# 🧪 Run specific test file
test-file FILE: build
    @echo "🧪 Running tests in {{FILE}}..."
    uv run python -m pytest {{FILE}} -v

# 🧪 Run tests with coverage
test-cov: build
    @echo "🧪 Running tests with coverage..."
    uv run python -m pytest tests/ --cov=ax_utils --cov-report=html --cov-report=term

# 🏃 Run quick functionality tests
test-quick: build
    @echo "🏃 Running quick functionality tests..."
    uv run python scripts/quick_test.py

# 🚀 Run performance benchmarks
benchmark: build
    @echo "🚀 Running performance benchmarks..."
    uv run python tests/test_benchmarks.py

# 🧪 Run integration tests
test-integration: build
    @echo "🧪 Running integration tests..."
    uv run python tests/test_integration.py

# 🧪 Run all original module tests (from ax_utils subdirectories)
test-original: build
    @echo "🧪 Running original module test suites..."
    uv run python -m pytest ax_utils/*/tests/ -v

# 🔍 Run linting and code quality checks
lint:
    @echo "🔍 Running linting checks..."
    uv run ruff check ax_utils/ tests/
    uv run ruff format --check ax_utils/ tests/

# 🔧 Auto-fix code formatting
format:
    @echo "🔧 Formatting code..."
    uv run ruff check --fix ax_utils/ tests/
    uv run ruff format ax_utils/ tests/
    @echo "✅ Code formatted"

# 🔬 Run type checking
typecheck:
    @echo "🔬 Running type checks..."
    uv run mypy ax_utils/ --ignore-missing-imports

# ✅ Run complete quality checks (lint + typecheck + test)
check: lint typecheck test
    @echo "✅ All quality checks passed!"

# 🚀 Install package in development mode
install-dev-package: build
    @echo "🚀 Installing package in development mode..."
    uv pip install -e .
    @echo "✅ Package installed in development mode"

# 📊 Show package info
info:
    @echo "📊 Package Information:"
    @echo "Name: ax_utils"
    @echo "Version: 3.0.2"
    @uv run python -c "import ax_utils; print(f'Location: {ax_utils.__file__}')" 2>/dev/null || echo "Package not installed"
    @echo ""
    @echo "📁 Directory structure:"
    @find ax_utils -name "*.py" -o -name "*.c" -o -name "*.cpp" | head -10
    @echo ""
    @echo "🔧 Build artifacts:"
    @find ax_utils -name "*.so" 2>/dev/null | wc -l | xargs echo "Compiled extensions:"

# 🧪 Test import and basic functionality (alias for test-quick)
test-import: test-quick

# 📋 Validate package for PyPI publishing
validate: clean dist
    @echo "📋 Validating package for PyPI..."
    uv run python -m twine check dist/*
    @echo "✅ Package validation complete"

# 🚀 Publish to PyPI (requires authentication)
publish: validate
    @echo "🚀 Publishing to PyPI..."
    @echo "⚠️  This will upload to PyPI. Make sure you're ready!"
    @read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
    uv publish dist/*
    @echo "✅ Package published to PyPI!"

# 🚀 Publish to Test PyPI (for testing)
publish-test: validate
    @echo "🚀 Publishing to Test PyPI..."
    uv publish --repository testpypi dist/*
    @echo "✅ Package published to Test PyPI!"

# 🔄 Full development cycle (clean, build, test, lint)
dev: clean build test-quick lint
    @echo "🔄 Development cycle complete!"

# 🚀 Full release cycle (clean, build, test, lint, dist, validate)
release: clean build test lint dist validate
    @echo "🚀 Release preparation complete!"
    @echo "📦 Files ready for release:"
    @ls -la dist/
    @echo ""
    @echo "Next steps:"
    @echo "  just publish-test  # Test on Test PyPI first"
    @echo "  just publish       # Publish to real PyPI"

# 🐛 Debug build issues
debug-build:
    @echo "🐛 Debug build information..."
    @echo "Python version:"
    @uv run python --version
    @echo ""
    @echo "Compiler information:"
    @which gcc || echo "gcc not found"
    @which clang || echo "clang not found"
    @echo ""
    @echo "Extension files:"
    @find ax_utils -name "*.c" -o -name "*.cpp"
    @echo ""
    @echo "Compiled extensions:"
    @find ax_utils -name "*.so" || echo "No compiled extensions found"
    @echo ""
    @echo "Build with verbose output:"
    uv run python setup.py build_ext --inplace --verbose

# 🧹 Deep clean (including uv cache)
clean-all: clean
    @echo "🧹 Deep cleaning (including uv cache)..."
    uv cache clean
    @echo "✅ Deep clean complete"

# 📊 Run complete test suite with reports
test-all: build
    @echo "📊 Running complete test suite..."
    uv run python -m pytest tests/ -v --tb=short --cov=ax_utils --cov-report=html --cov-report=term --cov-report=xml
    @echo "📊 Test reports generated:"
    @echo "  - HTML coverage: htmlcov/index.html"
    @echo "  - XML coverage: coverage.xml"

# 🏃 Quick development check (fast version of dev cycle)
quick: build test-quick
    @echo "🏃 Quick check complete!"

# 🔧 Setup development environment from scratch
setup: install-dev install-dev-package
    @echo "🔧 Development environment setup complete!"
    @echo "Available commands:"
    @just --list
