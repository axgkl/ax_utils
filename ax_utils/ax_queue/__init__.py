try:
    from ._ax_queue import Queue as AXQueue
    from ._ax_queue import Full
    from ._ax_queue import Empty
except:
    # maybe the cpp compilation failed, fall back to python:
    print ('AXQueue not available, falling back to standard Queue')
    from ax_utils.six.moves.queue import Queue as AXQueue
    from ax_utils.six.moves.queue import Full, Empty
