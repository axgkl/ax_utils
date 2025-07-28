# UV Cache Fix Documentation

## Issue: UV Cache Error on First Push

When you first push to GitHub, the workflows may fail with:
```
Error: No file matched to [**/uv.lock], make sure you have checked out the target repository
```

## Temporary Solution Applied

I've temporarily disabled UV caching in the workflows by setting `enable-cache: false`.

## Re-enable Caching Later (Optional)

Once your repository is established and has been running for a while, you can re-enable caching for better performance:

### In `.github/workflows/test.yml`:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
```

### In `.github/workflows/quality.yml`:
```yaml
- name: Install uv  
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
```

## Alternative: Conditional Caching

You can also use conditional caching that only enables when lock files exist:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: ${{ hashFiles('**/uv.lock') != '' }}
```

## Benefits of UV Caching

When re-enabled, UV caching provides:
- **Faster CI runs** (10-100x faster dependency installation)
- **Reduced GitHub Actions minutes** usage
- **More reliable builds** with consistent dependency versions

## Current Status

✅ **Workflows will run successfully** without caching  
⚠️ **Slightly slower** dependency installation (still fast with UV)  
🔄 **Can re-enable caching** once repository is established
