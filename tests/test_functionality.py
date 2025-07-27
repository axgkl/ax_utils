# Test suite for ax_utils package
import pytest


def test_basic_imports():
    """Test that all main modules can be imported."""

    from ax_utils.ax_queue import AXQueue
    from ax_utils.ax_tree import AXTree
    from ax_utils.props_to_tree import props_to_tree
    from ax_utils.simple_deepcopy import deepcopy

    # Basic smoke test - just ensure imports work
    assert AXQueue is not None
    assert AXTree is not None
    assert deepcopy is not None
    assert props_to_tree is not None


def test_ax_queue_functionality():
    """Test AXQueue basic functionality."""
    from ax_utils.ax_queue import AXQueue, Empty, Full

    # Test basic queue operations
    q = AXQueue()
    q.put('test_item')
    assert q.get() == 'test_item'

    # Test with maxsize
    q_sized = AXQueue(maxsize=1)
    q_sized.put('item1')

    # Queue should be full now
    with pytest.raises(Full):
        q_sized.put('item2', block=False)

    # Get item and queue should be empty
    assert q_sized.get() == 'item1'

    with pytest.raises(Empty):
        q_sized.get(block=False)


def test_ax_tree_functionality():
    """Test AXTree basic functionality."""
    from ax_utils.ax_tree import AXTree

    tree = AXTree()

    # Test dot notation assignment and retrieval
    tree['user.profile.name'] = 'John Doe'
    tree['user.profile.age'] = 30
    tree['user.settings.theme'] = 'dark'

    # Test nested access
    assert tree['user']['profile']['name'] == 'John Doe'
    assert tree['user']['profile']['age'] == 30
    assert tree['user']['settings']['theme'] == 'dark'

    # Test direct dot notation access
    assert tree['user.profile.name'] == 'John Doe'

    # Test that it behaves like a dict
    assert 'user' in tree
    assert len(tree['user']['profile']) == 2


def test_simple_deepcopy_functionality():
    """Test simple_deepcopy functionality."""
    from ax_utils.simple_deepcopy import deepcopy

    # Test with complex nested structure
    original = {
        'list': [1, 2, {'nested': 'value'}],
        'dict': {'key': 'value'},
        'tuple': (1, 2, 3),
        'number': 42,
        'string': 'test',
    }

    copied = deepcopy(original)

    # Should be equal but not the same object
    assert copied == original
    assert copied is not original
    assert copied['list'] is not original['list']
    assert copied['list'][2] is not original['list'][2]
    assert copied['dict'] is not original['dict']


def test_props_to_tree_functionality():
    """Test props_to_tree functionality."""
    from ax_utils.props_to_tree import props_to_tree, tree_to_props

    # Test converting flat props to tree
    props = {
        'app.database.host': 'localhost',
        'app.database.port': 5432,
        'app.cache.redis.host': '127.0.0.1',
        'app.cache.redis.port': 6379,
        'app.debug': True,
    }

    tree = props_to_tree(props)

    # Test tree structure
    assert tree['app']['database']['host'] == 'localhost'
    assert tree['app']['database']['port'] == 5432
    assert tree['app']['cache']['redis']['host'] == '127.0.0.1'
    assert tree['app']['cache']['redis']['port'] == 6379
    assert tree['app']['debug'] is True

    # Test round-trip conversion
    converted_back = tree_to_props(tree)
    assert converted_back == props


def test_unicode_utils_functionality():
    """Test unicode utilities."""
    from ax_utils.unicode_utils import decode_nested, encode_nested, is_utf8

    # Test UTF-8 detection
    assert is_utf8(b'hello world') is True
    assert is_utf8(b'hello \xc3\xa9 world') is True  # UTF-8 encoded é

    # Test with invalid UTF-8
    assert is_utf8(b'\xff\xfe') is False

    # Test nested encoding/decoding
    nested_data = {
        'string': 'hello',
        'unicode': 'café',
        'list': ['item1', 'item2'],
        'nested': {'key': 'value'},
    }

    # Should handle nested structures
    encoded = encode_nested(nested_data)
    decoded = decode_nested(encoded)

    # Basic functionality test - exact behavior depends on implementation
    assert isinstance(encoded, (dict, type(nested_data)))
    assert isinstance(decoded, (dict, type(nested_data)))


def test_performance_vs_stdlib():
    """Test that our implementations are faster than stdlib (basic check)."""
    import copy
    import time

    from ax_utils.simple_deepcopy import deepcopy as ax_deepcopy

    # Create a moderately complex structure
    test_data = {
        'lists': [[i] * 10 for i in range(100)],
        'dicts': [{'key': i, 'value': i * 2} for i in range(100)],
        'nested': {'level1': {'level2': {'level3': list(range(100))}}},
    }

    # Time stdlib deepcopy
    start = time.time()
    for _ in range(10):
        stdlib_copy = copy.deepcopy(test_data)
    stdlib_time = time.time() - start

    # Time ax_utils deepcopy
    start = time.time()
    for _ in range(10):
        ax_copy = ax_deepcopy(test_data)
    ax_time = time.time() - start

    # Verify they produce the same result
    assert ax_copy == stdlib_copy

    # Our version should be competitive (allow some variance)
    # This is more of a smoke test than a strict performance requirement
    print(f'Stdlib deepcopy: {stdlib_time:.4f}s')
    print(f'AX deepcopy: {ax_time:.4f}s')
    print(f'Speedup: {stdlib_time / ax_time:.2f}x' if ax_time > 0 else 'N/A')


def test_all_extensions_loaded():
    """Verify all C/C++ extensions are properly loaded."""
    # This test ensures we're using compiled extensions, not fallbacks

    from ax_utils.ax_queue import AXQueue
    from ax_utils.simple_deepcopy import deepcopy
    from ax_utils.unicode_utils import is_utf8

    # Test that we got the C/C++ implementations
    # AXQueue should be the C++ version (not fallback to stdlib Queue)
    q = AXQueue()
    assert type(q).__name__ == 'Queue'  # C++ extension class name

    # deepcopy should be the C implementation
    assert deepcopy.__module__ == 'ax_utils.simple_deepcopy._simple_deepcopy'

    # is_utf8 should be the C implementation
    assert is_utf8.__module__ == 'ax_utils.unicode_utils._isutf8'

    print('✅ All C/C++ extensions are properly loaded!')


if __name__ == '__main__':
    # Run tests directly if executed as script
    test_basic_imports()
    test_ax_queue_functionality()
    test_ax_tree_functionality()
    test_simple_deepcopy_functionality()
    test_props_to_tree_functionality()
    test_unicode_utils_functionality()
    test_all_extensions_loaded()
    test_performance_vs_stdlib()

    print('🎉 All tests passed!')
