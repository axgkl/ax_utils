# Performance benchmarks for ax_utils
import copy
import threading
import time
from contextlib import contextmanager


@contextmanager
def timer(name):
    """Context manager to time operations."""
    start = time.time()
    yield
    end = time.time()
    print(f'{name}: {end - start:.4f}s')


def benchmark_deepcopy():
    """Benchmark ax_utils.deepcopy vs stdlib copy.deepcopy."""
    from ax_utils.simple_deepcopy import deepcopy as ax_deepcopy

    # Create test data of varying complexity
    simple_data = {'a': 1, 'b': [1, 2, 3], 'c': 'string'}

    complex_data = {
        'lists': [[i] * 50 for i in range(200)],
        'dicts': [{'key' + str(j): j * i for j in range(20)} for i in range(50)],
        'nested': {
            'level1': {
                'level2': {
                    'level3': {
                        'data': list(range(1000)),
                        'more': {'x': list(range(100)) for x in range(10)},
                    }
                }
            }
        },
    }

    iterations = 100

    print('🚀 Deepcopy Benchmarks')
    print('=' * 50)

    # Simple data benchmark
    print('\n📊 Simple Data (100 iterations):')

    with timer('  stdlib copy.deepcopy'):
        for _ in range(iterations):
            copy.deepcopy(simple_data)

    with timer('  ax_utils.deepcopy   '):
        for _ in range(iterations):
            ax_deepcopy(simple_data)

    # Complex data benchmark
    print('\n📊 Complex Data (10 iterations):')

    with timer('  stdlib copy.deepcopy'):
        for _ in range(10):
            copy.deepcopy(complex_data)

    with timer('  ax_utils.deepcopy   '):
        for _ in range(10):
            ax_deepcopy(complex_data)


def benchmark_ax_queue():
    """Benchmark AXQueue performance."""
    import queue

    from ax_utils.ax_queue import AXQueue

    print('\n🚀 Queue Benchmarks')
    print('=' * 50)

    iterations = 100000

    # Single-threaded performance
    print(f'\n📊 Single-threaded ({iterations:,} operations):')

    # AXQueue
    q_ax = AXQueue()
    with timer('  AXQueue put/get'):
        for i in range(iterations):
            q_ax.put(i)
        for i in range(iterations):
            q_ax.get()

    # Stdlib Queue
    q_std = queue.Queue()
    with timer('  stdlib Queue   '):
        for i in range(iterations):
            q_std.put(i)
        for i in range(iterations):
            q_std.get()

    # Multi-threaded performance
    print(f'\n📊 Multi-threaded (4 threads, {iterations // 4:,} ops each):')

    def threaded_queue_test(queue_class, name):
        q = queue_class()

        def producer(count):
            for i in range(count):
                q.put(i)

        def consumer(count):
            for i in range(count):
                q.get()

        start_time = time.time()

        # Start producers and consumers
        threads = []
        ops_per_thread = iterations // 4

        for i in range(2):  # 2 producers
            t = threading.Thread(target=producer, args=(ops_per_thread,))
            threads.append(t)
            t.start()

        for i in range(2):  # 2 consumers
            t = threading.Thread(target=consumer, args=(ops_per_thread,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = time.time()
        print(f'  {name}: {end_time - start_time:.4f}s')

    threaded_queue_test(AXQueue, 'AXQueue threaded')
    threaded_queue_test(queue.Queue, 'stdlib Queue   ')


def benchmark_ax_tree():
    """Benchmark AXTree performance."""
    from ax_utils.ax_tree import AXTree

    print('\n🚀 AXTree Benchmarks')
    print('=' * 50)

    iterations = 50000

    # Tree vs dict performance
    print(f'\n📊 Tree Operations ({iterations:,} operations):')

    # AXTree
    tree = AXTree()
    with timer('  AXTree set/get'):
        for i in range(iterations):
            tree[f'level1.level2.key{i}'] = i
        for i in range(iterations):
            val = tree[f'level1.level2.key{i}']

    # Regular dict (for comparison, though not equivalent)
    regular_dict = {}
    with timer('  dict set/get  '):
        for i in range(iterations):
            regular_dict[f'level1.level2.key{i}'] = i
        for i in range(iterations):
            val = regular_dict[f'level1.level2.key{i}']


def benchmark_props_to_tree():
    """Benchmark props_to_tree conversion."""
    from ax_utils.props_to_tree import props_to_tree, tree_to_props

    print('\n🚀 Props-to-Tree Benchmarks')
    print('=' * 50)

    # Create test props
    props = {}
    for i in range(1000):
        props[f'section{i % 10}.subsection{i % 5}.key{i}'] = f'value{i}'

    iterations = 100

    print(f'\n📊 Conversion Performance ({iterations} iterations, 1000 props):')

    with timer('  props_to_tree'):
        for _ in range(iterations):
            tree = props_to_tree(props)

    # Convert once for tree_to_props test
    tree = props_to_tree(props)

    with timer('  tree_to_props'):
        for _ in range(iterations):
            back_to_props = tree_to_props(tree)


def benchmark_unicode_utils():
    """Benchmark unicode utilities."""
    from ax_utils.unicode_utils import decode_nested, encode_nested, is_utf8

    print('\n🚀 Unicode Utils Benchmarks')
    print('=' * 50)

    # Test data
    utf8_strings = [
        b'hello world',
        b'caf\xc3\xa9',  # café
        b'\xe2\x82\xac\xf0\x9f\x98\x80',  # €😀
        b'simple ascii',
        b'\xf0\x9f\x8c\x8d\xf0\x9f\x8c\x8e\xf0\x9f\x8c\x8f',  # 🌍🌎🌏
    ] * 1000

    iterations = 10000

    print(f'\n📊 UTF-8 Detection ({iterations:,} checks):')

    with timer('  is_utf8'):
        for _ in range(iterations // len(utf8_strings)):
            for s in utf8_strings:
                is_utf8(s)

    # Nested encoding/decoding
    nested_data = {
        'strings': ['hello', 'world', 'café', '🌍'],
        'nested': {
            'more_strings': ['test1', 'test2'],
            'deep': {'values': ['a', 'b', 'c']},
        },
        'list': [f'item{i}' for i in range(100)],
    }

    print('\n📊 Nested Encoding/Decoding (1000 iterations):')

    with timer('  encode_nested'):
        for _ in range(1000):
            encoded = encode_nested(nested_data)

    encoded = encode_nested(nested_data)
    with timer('  decode_nested'):
        for _ in range(1000):
            decoded = decode_nested(encoded)


def run_all_benchmarks():
    """Run complete benchmark suite."""
    print('🏁 ax_utils Performance Benchmark Suite')
    print('=' * 60)

    try:
        benchmark_deepcopy()
        benchmark_ax_queue()
        benchmark_ax_tree()
        benchmark_props_to_tree()
        benchmark_unicode_utils()

        print('\n' + '=' * 60)
        print('✅ All benchmarks completed successfully!')
        print('\nNote: Performance will vary based on system specs.')
        print('These benchmarks show relative performance between implementations.')

    except Exception as e:
        print(f'\n❌ Benchmark failed: {e}')
        raise


if __name__ == '__main__':
    run_all_benchmarks()
