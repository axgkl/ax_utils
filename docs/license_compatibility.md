# License Configuration Compatibility

## Issue: Python 3.8 License Format Error

When running on Python 3.8, you may encounter this setuptools error:
```
configuration error: `project.license` must be valid exactly by one definition
```

## Root Cause

Different Python/setuptools versions have different requirements for license specification:

- **Python 3.8** (older setuptools): Requires `{text = "..."}` or `{file = "..."}` format
- **Python 3.9+** (newer setuptools): Supports simple string `"BSD-3-Clause"` format

## Current Solution

We use the **table format** for maximum compatibility:
```toml
license = {text = "BSD-3-Clause"}
```

This format:
- ✅ **Works on Python 3.8-3.12**
- ✅ **Provides proper license attribution**
- ⚠️ **Shows deprecation warning on newer Python** (but still works)

## Alternative Approaches

### Option 1: License File Reference
```toml
license = {file = "LICENSE"}
```
- More future-proof
- Requires LICENSE file to be properly formatted

### Option 2: Modern SPDX (Python 3.9+ only)
```toml
license = "BSD-3-Clause"
```
- Cleaner format
- **Breaks Python 3.8 compatibility**

### Option 3: Conditional (Complex)
Use different formats based on Python version - not recommended for simplicity.

## Recommendation

**Keep current format** until Python 3.8 support is dropped. The deprecation warning is harmless and the functionality works correctly across all supported Python versions.

## When to Change

Consider updating to modern format when:
- Python 3.8 support is no longer needed
- All CI environments use Python 3.9+
- setuptools>=77.0.0 is minimum requirement

## Current Status

✅ **Compatible across Python 3.8-3.12**  
✅ **GitHub Actions pass on all versions**  
⚠️ **Deprecation warning on Python 3.12** (harmless)  
🔄 **Can modernize when dropping Python 3.8**
