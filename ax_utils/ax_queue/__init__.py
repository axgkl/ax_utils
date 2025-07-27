try:
    from ._ax_queue import Empty, Full, Queue as AXQueue
except:
    # maybe the cpp compilation failed, fall back to python:
    print('AXQueue not available, falling back to standard Queue')
    from queue import Empty, Full, Queue as AXQueue
