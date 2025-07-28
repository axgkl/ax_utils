# Windows Compatibility Status

## Current Status: Not Supported

Windows has been removed from the CI test matrix due to build failures.

## Issues Encountered

1. **C/C++ Compilation**: The package includes C/C++ extensions that may have compatibility issues on Windows
2. **Build Tools**: Windows requires specific Visual Studio build tools that aren't configured
3. **CI Complexity**: Windows builds were adding significant complexity to the CI pipeline

## Supported Platforms

- ✅ **Linux** (ubuntu-latest)
- ✅ **macOS** (macos-latest)  
- ❌ **Windows** (not currently supported)

## Future Windows Support

To add Windows support in the future:

### Option 1: Add Windows Build Tools
```yaml
# In .github/workflows/test.yml
- name: Set up Visual C++ (Windows)
  if: runner.os == 'Windows'
  uses: microsoft/setup-msbuild@v1
```

### Option 2: Use conda-forge for Windows
```yaml
# Use conda instead of UV for Windows builds
- name: Setup Miniconda (Windows)
  if: runner.os == 'Windows'  
  uses: conda-incubator/setup-miniconda@v2
```

### Option 3: Pre-built Wheels
- Build Windows wheels on a dedicated Windows machine
- Upload to PyPI for Windows users
- Skip compilation in CI, just test installation

## C/C++ Extension Considerations

The package includes these C/C++ extensions that need Windows compatibility:
- `ax_utils.props_to_tree._props_to_tree`
- `ax_utils.ax_tree._ax_tree`  
- `ax_utils.ax_queue._ax_queue`
- `ax_utils.unicode_utils._convert_nested`
- `ax_utils.unicode_utils._isutf8`
- `ax_utils.simple_deepcopy._simple_deepcopy`

Each would need Windows-specific build configuration in `setup.py`.

## Current Recommendation

**Focus on Linux/macOS support** where the package works reliably. Windows support can be added later if there's user demand and resources for proper testing/maintenance.

## User Workarounds

Windows users who want to try the package can:
1. **Use WSL2** (Windows Subsystem for Linux)
2. **Use Docker** with Linux container
3. **Use virtual machine** with Linux

These approaches provide the supported Linux environment on Windows hardware.
