# GitHub Actions CI/CD Setup

This document explains the GitHub Actions workflows configured for the ax_utils project.

## Workflows Overview

### 1. Tests Workflow (`test.yml`)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches  
- Manual workflow dispatch

**Matrix Testing:**
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating systems**: Ubuntu, macOS, Windows
- **Total combinations**: 15 test environments

**Test Steps:**
1. **Code checkout** and Python setup
2. **UV installation** for fast dependency management
3. **C/C++ extension building** for performance components
4. **Code quality checks** (Ruff linting and formatting)
5. **Type checking** with MyPy
6. **Unit tests** with pytest
7. **Functionality verification** with import and basic usage tests

**Coverage Reporting:**
- Separate job for test coverage analysis
- Uploads results to Codecov
- Runs on Ubuntu with Python 3.11

**Performance Benchmarks:**
- Runs only on main branch pushes
- Provides performance regression detection
- Uses optimized Ubuntu environment

### 2. Code Quality Workflow (`quality.yml`)

**Purpose:** Focused code quality and security checks

**Quality Checks:**
- **Ruff linting** with GitHub-formatted output
- **Ruff formatting** consistency verification
- **MyPy type checking** for type safety
- **Bandit security scanning** for common vulnerabilities
- **Safety dependency checking** for known CVEs

**Artifacts:**
- Security scan results (JSON format)
- Vulnerability scan results for review

### 3. Build and Release Workflow (`release.yml`)

**Triggers:**
- Git tags starting with `v*` (e.g., `v3.0.3`)
- Manual workflow dispatch

**Build Process:**
1. **Multi-platform wheel building** (Ubuntu, macOS, Windows)
2. **Wheel testing** across all Python versions
3. **PyPI release** (requires manual tag push)

**Security:**
- Uses PyPI API tokens stored in GitHub secrets
- Requires `release` environment for additional protection

### 4. Dependabot Configuration

**Automated Updates:**
- **Python dependencies**: Weekly on Mondays
- **GitHub Actions**: Weekly updates for workflow actions
- **Pull request limits**: 5 for dependencies, 3 for actions
- **Automatic reviewers**: Configurable team members

## Badges Explained

```markdown
[![Tests](https://github.com/axgkl/ax_utils/workflows/Tests/badge.svg)](https://github.com/axgkl/ax_utils/actions/workflows/test.yml)
```
- Shows test status (passing/failing) for the main branch
- Links to latest test run results

```markdown
[![Python versions](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://pypi.org/project/ax_utils/)
```
- Displays supported Python versions (3.8+)
- Links to PyPI package page

```markdown
[![PyPI version](https://badge.fury.io/py/ax_utils.svg)](https://badge.fury.io/py/ax_utils)
```
- Shows latest PyPI version
- Auto-updates when new versions are released

```markdown
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
```
- Displays project license (MIT)
- Links to license file

```markdown
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```
- Indicates Ruff is used for code formatting and linting
- Links to Ruff project

## Setup Instructions

### 1. Repository Configuration

After pushing to GitHub, configure these repository settings:

**Secrets (Settings → Secrets and variables → Actions):**
```
PYPI_API_TOKEN=your_pypi_token_here
CODECOV_TOKEN=your_codecov_token_here  # Optional
```

**Environments (Settings → Environments):**
- Create `release` environment
- Add protection rules (require reviewers for releases)
- Add `PYPI_API_TOKEN` to release environment secrets

### 2. Branch Protection

**Recommended branch protection for `main`:**
- Require status checks before merging
- Require up-to-date branches
- Required status checks:
  - `Test Python 3.8 on ubuntu-latest`
  - `Test Python 3.11 on ubuntu-latest` 
  - `Code Quality Checks`

### 3. PyPI Token Setup

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create API token with scope limited to `ax_utils` project
3. Add token to GitHub repository secrets as `PYPI_API_TOKEN`

### 4. Codecov Integration (Optional)

1. Visit [Codecov.io](https://codecov.io/)
2. Connect your GitHub repository
3. Add `CODECOV_TOKEN` to repository secrets
4. Configure coverage thresholds in `codecov.yml` if desired

## Usage Examples

### Running Tests Locally

```bash
# Install dependencies
uv sync --dev

# Build extensions
uv run python setup.py build_ext --inplace

# Run all checks (matching CI)
just lint          # Code quality
just typecheck     # Type checking  
just test          # Unit tests
just test-quick    # Quick functionality tests
```

### Manual Release Process

```bash
# Create and push a version tag
git tag v3.0.3
git push origin v3.0.3

# This triggers the release workflow automatically
# Monitor progress at: https://github.com/axgkl/ax_utils/actions
```

### Badge Updates

Update badges in `README.md` by replacing `axgkl` with your actual GitHub username/organization:

```markdown
[![Tests](https://github.com/axgkl/ax_utils/workflows/Tests/badge.svg)](https://github.com/axgkl/ax_utils/actions/workflows/test.yml)
```

## Performance Considerations

### Fast CI with UV

- **UV package manager**: 10-100x faster than pip
- **Dependency caching**: Reduces installation time
- **Lock file usage**: Ensures reproducible builds

### Optimized Test Matrix

- **Fail-fast disabled**: Shows all platform/version failures
- **Strategic OS selection**: Ubuntu for speed, macOS/Windows for compatibility
- **Coverage on single platform**: Avoids redundant coverage runs

### Efficient Workflows

- **Parallel jobs**: Test matrix runs in parallel
- **Conditional jobs**: Benchmarks only run on main branch
- **Artifact upload**: Preserves build outputs for debugging

## Troubleshooting

### Common Issues

**C++ Compilation Failures:**
- Ensure development tools are available on all platforms
- Check compiler compatibility with Python versions
- Review build logs in Actions tab

**Import Failures:**
- Verify C++ extensions built successfully
- Check Python path and module installation
- Review import test outputs in workflow logs

**Badge Not Updating:**
- Check workflow names match badge URLs exactly
- Ensure workflows are enabled in repository settings
- Verify badge URLs point to correct repository

**Release Failures:**
- Confirm PyPI token has correct permissions
- Check version number format (must start with 'v')
- Verify all tests pass before tagging

This CI/CD setup provides comprehensive testing, quality assurance, and automated releases while maintaining fast feedback cycles for development.
