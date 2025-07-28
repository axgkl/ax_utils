# GitHub Actions Artifact v3 Deprecation Fix

## Issue: Deprecated Artifact Actions

GitHub deprecated v3 of the artifact actions in April 2024:
```
Error: This request has been automatically failed because it uses a deprecated version of `actions/upload-artifact: v3`
```

## Root Cause

GitHub sunset support for artifact actions v3:
- **upload-artifact@v3** ❌ Deprecated
- **download-artifact@v3** ❌ Deprecated

## Solution Applied

### ✅ **Updated All Artifact Actions to v4**

**Before (Deprecated):**
```yaml
- name: Upload coverage reports
  uses: actions/upload-artifact@v3
  with:
    name: coverage-reports
    path: htmlcov/

- name: Download build artifacts  
  uses: actions/download-artifact@v3
  with:
    name: wheels
```

**After (Current):**
```yaml
- name: Upload coverage reports
  uses: actions/upload-artifact@v4
  with:
    name: coverage-reports
    path: htmlcov/

- name: Download build artifacts
  uses: actions/download-artifact@v4
  with:
    name: wheels
```

### 🚀 **Other GitHub Actions Updates**

While updating, also modernized other actions:
- **setup-python**: v4 → v5 (latest)
- **checkout**: Already v4 (current)
- **astral-sh/setup-uv**: Already v4 (current)

## Key Differences in v4

### Upload Artifact Changes
- **Better performance**: Faster uploads and downloads
- **Improved compression**: Smaller artifact sizes
- **Better error handling**: More descriptive error messages

### Download Artifact Changes  
- **Automatic extraction**: No need to manually extract archives
- **Pattern matching**: Better support for downloading specific files
- **Merge behavior**: Improved handling of multiple artifacts

## Files Updated

1. **`.github/workflows/release.yml`**:
   - upload-artifact@v3 → v4
   - download-artifact@v3 → v4 (2 occurrences)

2. **`.github/workflows/quality.yml`**:
   - upload-artifact@v3 → v4 (2 occurrences)

3. **All workflows**:
   - setup-python@v4 → v5

## Verification

✅ **Actions now use supported versions**  
✅ **No breaking changes to functionality**  
✅ **Improved performance and reliability**  
✅ **Future-proofed against next deprecation cycle**

## Best Practices

1. **Pin to major versions**: Use `@v4` not `@v4.3.1` for automatic patches
2. **Monitor deprecations**: Watch GitHub's changelog for deprecation notices
3. **Update regularly**: Don't wait until forced deprecation
4. **Test after updates**: Verify workflows still work as expected

GitHub typically provides 6-12 months notice before forcing deprecation, so staying current helps avoid sudden breakages.
