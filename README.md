# ax_utils - High-Performance Python Utilities

[![Tests](https://github.com/axgkl/ax_utils/workflows/Tests/badge.svg)](https://github.com/axgkl/ax_utils/actions/workflows/test.yml)
[![Python versions](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://pypi.org/project/ax_utils/)
[![PyPI version](https://badge.fury.io/py/axiros_utils.svg)](https://badge.fury.io/py/axiros_utils)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A standalone Python package providing high-performance utilities with C/C++ extensions, converted from the original `ax.utils` namespace package.

Author: **Stephan Bentheimer** 

## Features

- **AXQueue**: High-performance thread-safe queue implementation with C++ backend
- **AXTree**: Fast tree data structure with C extensions for efficient nested data manipulation
- **Simple Deepcopy**: Optimized deep copy implementation
- **Props to Tree**: Convert flat property notation to nested tree structures
- **Unicode Utils**: Fast Unicode processing utilities
- **Gevent Integration**: Seamless integration with gevent for async applications

## Installation

```bash
pip install axiros-utils
```

The package includes C/C++ extensions that will be compiled during installation, providing significant performance improvements over pure Python implementations.

## Troubleshoot Installation

Problem: Compile fail on darwin.

```
[stderr]
      ax_utils/ax_queue/_ax_queue.cpp:4:10: fatal error: 'exception' file
      not found
          4 | #include <exception>
            |          ^~~
      1 error generated.
      error: command '/usr/bin/clang++' failed with exit code 1
```
With `Python 3.11.13 (main, Jun  3 2025, 18:38:25) [Clang 17.0.0 (clang-1700.0.13.3)]` on darwin

Solution: Refresh your compiler tools. E.g. `xcode-select --install`.

The [tests](https://github.com/axgkl/ax_utils/actions) contain a few tests on osx.




## Quick Start

```python
from ax_utils.ax_queue import AXQueue
from ax_utils.ax_tree import AXTree
from ax_utils.simple_deepcopy import deepcopy
from ax_utils.props_to_tree import props_to_tree

# High-performance queue
queue = AXQueue()
queue.put("hello")
print(queue.get())  # "hello"

# Tree data structure with dot notation
tree = AXTree()
tree['user.profile.name'] = 'John'
print(tree['user']['profile']['name'])  # 'John'

# Fast deep copy
data = {'complex': [1, 2, {'nested': 'value'}]}
copied = deepcopy(data)

# Convert flat properties to tree
props = {'app.database.host': 'localhost', 'app.database.port': 5432}
tree_data = props_to_tree(props)
```

## Performance

All core operations are implemented in C/C++ for maximum performance:

- **AXQueue**: C++ implementation with std::mutex for thread safety
- **AXTree**: C implementation for fast tree operations
- **Unicode processing**: C implementations for encoding/decoding operations
- **Deep copy**: Optimized C implementation

## Compatibility

- Python 3.9+
- Linux and macOS
- Automatic compilation during pip install

## Migration from ax.utils

If you're migrating from the original `ax.utils` namespace package:

```python
# Old imports
from ax.utils.ax_queue import AXQueue
from ax.utils.ax_tree import AXTree

# New imports
from ax_utils.ax_queue import AXQueue
from ax_utils.ax_tree import AXTree
```

## Development

The package uses modern Python packaging with `pyproject.toml` and supports development installation:

```bash
# Clone and install in development mode
git clone <repository>
cd ax_utils
pip install -e .
```


## License

BSD-3-Clause license (incl. Axiros attribution obligation).
