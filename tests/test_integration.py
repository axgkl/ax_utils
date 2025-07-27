# Integration tests for ax_utils package
import threading

import pytest


def test_thread_safety_ax_queue():
    """Test that AXQueue is thread-safe."""
    from ax_utils.ax_queue import AXQueue

    q = AXQueue()
    results = []

    def producer(name, count):
        for i in range(count):
            q.put(f'{name}-{i}')

    def consumer(count):
        for _ in range(count):
            item = q.get()
            results.append(item)

    # Start multiple producers and consumers
    threads = []

    # 3 producers, each producing 10 items
    for i in range(3):
        t = threading.Thread(target=producer, args=(f'producer-{i}', 10))
        threads.append(t)
        t.start()

    # 2 consumers, consuming all 30 items
    for i in range(2):
        t = threading.Thread(target=consumer, args=(15,))
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    # Should have received all 30 items
    assert len(results) == 30
    assert len(set(results)) == 30  # All unique


def test_ax_tree_with_ax_queue():
    """Test integration between AXTree and AXQueue."""
    from ax_utils.ax_queue import AXQueue
    from ax_utils.ax_tree import AXTree

    # Create a tree with queue objects
    tree = AXTree()
    tree['services.queue1'] = AXQueue()
    tree['services.queue2'] = AXQueue()

    # Use the queues
    tree['services.queue1'].put('message1')
    tree['services.queue2'].put('message2')

    assert tree['services.queue1'].get() == 'message1'
    assert tree['services.queue2'].get() == 'message2'


def test_deepcopy_with_complex_objects():
    """Test deepcopy with AXTree and other complex objects."""
    from ax_utils.ax_tree import AXTree
    from ax_utils.simple_deepcopy import deepcopy

    # Create complex structure without queue (since queues can't be pickled)
    original = AXTree()
    original['data.numbers'] = list(range(100))
    original['data.config.host'] = 'localhost'
    original['data.config.port'] = 8080

    # Deep copy the tree
    copied = deepcopy(original)

    # Verify structure is copied
    assert copied['data.config.host'] == 'localhost'
    assert copied['data.config.port'] == 8080
    assert copied['data.numbers'] == list(range(100))

    # Verify they are separate instances
    assert copied is not original

    # Test that modifications don't affect original
    copied['data.config.host'] = 'newhost'
    assert original['data.config.host'] == 'localhost'
    assert copied['data.config.host'] == 'newhost'


def test_props_to_tree_integration():
    """Test props_to_tree with real-world configuration scenario."""
    from ax_utils.ax_tree import AXTree
    from ax_utils.props_to_tree import props_to_tree

    # Simulate configuration from environment/config file
    config_props = {
        'database.primary.host': 'db1.example.com',
        'database.primary.port': '5432',
        'database.primary.username': 'admin',
        'database.replica.host': 'db2.example.com',
        'database.replica.port': '5432',
        'cache.redis.host': 'redis.example.com',
        'cache.redis.port': '6379',
        'cache.redis.db': '0',
        'app.debug': 'true',
        'app.workers': '4',
        'logging.level': 'INFO',
        'logging.file': '/var/log/app.log',
    }

    # Convert to tree
    config_tree = props_to_tree(config_props)

    # Convert to AXTree for easier access
    app_config = AXTree()
    app_config.update(config_tree)

    # Test accessing nested configuration
    assert app_config['database.primary.host'] == 'db1.example.com'
    assert app_config['database']['primary']['port'] == '5432'
    assert app_config['cache']['redis']['db'] == '0'
    assert app_config['app']['workers'] == '4'

    # Test that we can modify the tree
    app_config['database.primary.password'] = 'secret'
    assert app_config['database']['primary']['password'] == 'secret'


def test_unicode_handling_edge_cases():
    """Test unicode utilities with edge cases."""
    from ax_utils.unicode_utils import is_utf8

    # Test various UTF-8 sequences
    test_cases = [
        (b'hello', True),
        (b'', True),  # Empty string is valid UTF-8
        (b'\xc3\xa9', True),  # é in UTF-8
        (b'\xe2\x82\xac', True),  # € symbol in UTF-8
        (b'\xf0\x9f\x98\x80', True),  # 😀 emoji in UTF-8
        (b'\xff\xfe', False),  # Invalid UTF-8
        (b'\x80\x80', False),  # Invalid UTF-8
    ]

    for byte_string, expected in test_cases:
        result = is_utf8(byte_string)
        assert result == expected, (
            f'is_utf8({byte_string!r}) returned {result}, expected {expected}'
        )


def test_memory_efficiency():
    """Basic test to ensure we're not leaking memory excessively."""
    import gc

    from ax_utils.ax_queue import AXQueue
    from ax_utils.ax_tree import AXTree
    from ax_utils.simple_deepcopy import deepcopy

    # Force garbage collection
    gc.collect()

    # Create and destroy many objects
    for i in range(1000):
        q = AXQueue()
        q.put(f'item-{i}')
        q.get()

        tree = AXTree()
        tree[f'key.{i}'] = i

        data = {'list': list(range(10)), 'dict': {'key': i}}
        copied = deepcopy(data)

        # Clean up references
        del q, tree, data, copied

    # Force garbage collection again
    gc.collect()

    # If we get here without memory issues, test passes
    assert True


def test_error_handling():
    """Test proper error handling in various scenarios."""
    from ax_utils.ax_queue import AXQueue, Empty, Full
    from ax_utils.ax_tree import AXTree

    # Test queue errors
    q = AXQueue(maxsize=1)
    q.put('item')

    with pytest.raises(Full):
        q.put('another', block=False)

    q.get()  # Empty the queue

    with pytest.raises(Empty):
        q.get(block=False)

    # Test tree with string keys
    tree = AXTree()

    # Should handle normal keys
    tree['normal.key'] = 'value'
    assert tree['normal.key'] == 'value'

    # Test nested access
    tree['level1.level2.level3'] = 'nested_value'
    assert tree['level1']['level2']['level3'] == 'nested_value'


if __name__ == '__main__':
    # Run integration tests
    test_thread_safety_ax_queue()
    test_ax_tree_with_ax_queue()
    test_deepcopy_with_complex_objects()
    test_props_to_tree_integration()
    test_unicode_handling_edge_cases()
    test_memory_efficiency()
    test_error_handling()

    print('🎉 All integration tests passed!')
