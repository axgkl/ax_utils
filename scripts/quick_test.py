#!/usr/bin/env python3
"""Quick import and functionality test for ax_utils."""

def main():
    print("🧪 Testing basic imports and functionality...")
    
    try:
        import ax_utils
        from ax_utils.ax_queue import AXQueue
        from ax_utils.ax_tree import AXTree
        from ax_utils.simple_deepcopy import deepcopy
        from ax_utils.props_to_tree import props_to_tree
        from ax_utils.unicode_utils import is_utf8
        
        print("✅ All imports successful")
        
        # Quick functionality tests
        q = AXQueue()
        q.put('test')
        assert q.get() == 'test'
        print("✅ AXQueue working")
        
        tree = AXTree()
        tree['a.b.c'] = 42
        assert tree['a']['b']['c'] == 42
        print("✅ AXTree working")
        
        data = [1, {'nested': 'data'}]
        copied = deepcopy(data)
        assert copied == data and copied is not data
        print("✅ deepcopy working")
        
        props = {'x.y': 1}
        result = props_to_tree(props)
        assert result['x']['y'] == 1
        print("✅ props_to_tree working")
        
        assert is_utf8(b'hello')
        print("✅ Unicode utils working")
        
        print("🎉 All basic functionality verified!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
