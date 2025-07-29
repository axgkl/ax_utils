# ax_utils development tasks (uv-native)
# Requires: just (https://github.com/casey/just) and uv
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
    rm -rf .uv-cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.so" -delete 2>/dev/null || true
    @echo "✅ Clean complete"

# 🔧 Sync development dependencies (uv native)
sync:
    @echo "🔧 Syncing dependencies..."
    uv sync --group dev
    @echo "✅ Dependencies synced"

# 🔧 Install development dependencies (legacy compatibility)
install-dev: sync

# 🏗️ Build C/C++ extensions in-place for development
build:
    @echo "🏗️ Building C/C++ extensions..."
    uv run python setup.py build_ext --inplace
    @echo "✅ Extensions built successfully"

# 📦 Build distribution packages (source + wheel) - uv native
dist: clean
    @echo "📦 Building distribution packages with uv..."
    uv build
    @echo "✅ Distribution packages built:"
    @ls -la dist/

# 🧪 Run all tests
test: build
    @echo "🧪 Running test suite..."
    uv run --group test pytest tests/ -v --tb=short

# 🧪 Run specific test file
test-file FILE: build
    @echo "🧪 Running tests in {{FILE}}..."
    uv run --group test pytest {{FILE}} -v

# 🧪 Run tests with coverage
test-cov: build
    @echo "🧪 Running tests with coverage..."
    uv run --group test pytest tests/ --cov=ax_utils --cov-report=html --cov-report=term

# 🏃 Run quick functionality tests
test-quick: build
    @echo "🏃 Running quick functionality tests..."
    uv run python scripts/quick_test.py

# 🚀 Run performance benchmarks
benchmark: build
    @echo "🚀 Running performance benchmarks..."
    uv run --group dev pytest tests/test_benchmarks.py -v --benchmark-only

# 🧪 Run integration tests
test-integration: build
    @echo "🧪 Running integration tests..."
    uv run --group test pytest tests/test_integration.py

# 🧪 Run all original module tests (from ax_utils subdirectories)
test-original: build
    @echo "🧪 Running original module test suites..."
    uv run --group test pytest ax_utils/*/tests/ -v

# 🔍 Run linting and code quality checks
lint:
    @echo "🔍 Running linting checks..."
    uv run --group dev ruff check ax_utils/ tests/
    uv run --group dev ruff format --check ax_utils/ tests/

# 🔧 Auto-fix code formatting
format:
    @echo "🔧 Formatting code..."
    uv run --group dev ruff check --fix ax_utils/ tests/
    uv run --group dev ruff format ax_utils/ tests/
    @echo "✅ Code formatted"

# 🔬 Run type checking
typecheck:
    @echo "🔬 Running type checks..."
    uv run --group dev mypy ax_utils/ --ignore-missing-imports

# ✅ Run complete quality checks (lint + typecheck + test)
check: lint typecheck test
    @echo "✅ All quality checks passed!"

# 🚀 Install package in development mode (uv native)
install-editable:
    @echo "🚀 Installing package in editable mode..."
    uv pip install -e .
    @echo "✅ Package installed in editable mode"

# 🚀 Install package in development mode (legacy alias)
install-dev-package: install-editable

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
    @echo ""
    @echo "📦 uv project info:"
    @uv tree --group dev | head -20

# 🧪 Test import and basic functionality (alias for test-quick)
test-import: test-quick

# 📋 Validate package for PyPI publishing
validate: clean dist
    @echo "📋 Validating package for PyPI..."
    uv run --group dev twine check dist/*
    @echo "✅ Package validation complete"

# 🚀 Publish to PyPI (requires authentication) - uv native
publish: dist
    @echo "🚀 Publishing to PyPI with uv..."
    @echo "⚠️  This will upload to PyPI. Make sure you're ready!"
    @read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
    uv publish --token "$(pass pypitoken)" dist/*
    @echo "✅ Package published to PyPI!"

# 🚀 Publish to Test PyPI (for testing) - uv native
publish-test: dist
    @echo "🚀 Publishing to Test PyPI with uv..."
    uv publish --repository testpypi dist/*
    @echo "✅ Package published to Test PyPI!"

# 🔄 Full development cycle (clean, build, test, lint)
dev: clean sync build test-quick lint
    @echo "🔄 Development cycle complete!"

# 🚀 Full release cycle (clean, build, test, lint, dist) - bypasses validation due to nh3 issue
release: clean sync build test lint dist
    @echo "🚀 Release preparation complete!"
    @echo "📦 Files ready for release:"
    @ls -la dist/
    @echo ""
    @echo "Next steps:"
    @echo "  just publish-test  # Test on Test PyPI first"
    @echo "  just publish       # Publish to real PyPI"
    @echo "  just validate      # Optional validation (has known nh3 issue)"

# 🐛 Debug build issues
debug-build:
    @echo "🐛 Debug build information..."
    @echo "Python version:"
    @uv run python --version
    @echo ""
    @echo "uv version:"
    @uv --version
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
    @echo "uv environment info:"
    @uv python list
    @echo ""
    @echo "Build with verbose output:"
    uv run python setup.py build_ext --inplace --verbose

# 🧹 Deep clean (including uv cache)
clean-all: clean
    @echo "🧹 Deep cleaning (including uv cache)..."
    uv cache clean
    rm -rf .uv-cache/
    @echo "✅ Deep clean complete"

# 📊 Run complete test suite with reports
test-all: build
    @echo "📊 Running complete test suite..."
    uv run --group dev pytest tests/ -v --tb=short --cov=ax_utils --cov-report=html --cov-report=term --cov-report=xml
    @echo "📊 Test reports generated:"
    @echo "  - HTML coverage: htmlcov/index.html"
    @echo "  - XML coverage: coverage.xml"

# 🏃 Quick development check (fast version of dev cycle)
quick: build test-quick
    @echo "🏃 Quick check complete!"

# 🔧 Setup development environment from scratch (uv native)
setup:
    @echo "🔧 Setting up development environment with uv..."
    uv sync --group dev
    uv pip install -e .
    @echo "🔧 Development environment setup complete!"
    @echo ""
    @echo "🎯 Available commands:"
    @just --list

# 🔍 Show dependency tree
deps:
    @echo "🔍 Dependency tree:"
    uv tree --group dev

# 🔄 Update dependencies to latest compatible versions
update:
    @echo "🔄 Updating dependencies..."
    uv lock --upgrade
    uv sync --group dev
    @echo "✅ Dependencies updated"

# 🚀 Run in production mode (no dev dependencies)
run-prod:
    @echo "🚀 Running with production dependencies only..."
    uv run --no-group python -c "import ax_utils; print('ax_utils loaded successfully')"

# 🔧 Add new dependency
add DEP:
    @echo "🔧 Adding dependency: {{DEP}}"
    uv add {{DEP}}

# 🔧 Add new dev dependency
add-dev DEP:
    @echo "🔧 Adding dev dependency: {{DEP}}"
    uv add --group dev {{DEP}}

# 🗑️ Remove dependency
remove DEP:
    @echo "🗑️ Removing dependency: {{DEP}}"
    uv remove {{DEP}}
