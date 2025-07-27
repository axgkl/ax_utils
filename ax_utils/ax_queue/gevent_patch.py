"""AXQueue is not gevent-friendly.

pool = AXQueue()

# greenlet-1
pool.get()

# greenlet-2
pool.put(None)

If greenlet-1 gets scheduled first the gevent-event-loop is blocked forever.
Since `pool.get()` uses a C++ std::mutex which blocks the entire thread.
Which means: greenlet-2 never gets scheduled.

Keep in mind. Gevent is cooperative multitasking. All greenlets run in the same
thread and a blocking call needs to give control back to the event-loop.
A C++ std::mutex is *NOT* doing that!!!
"""

import importlib

import gevent.monkey
import gevent.queue


def patch(event=None):
    to_patch = importlib.import_module('ax_utils.ax_queue')
    gevent.monkey.patch_item(to_patch, 'AXQueue', gevent.queue.Queue)
    gevent.monkey.patch_item(to_patch, 'Full', gevent.queue.Full)
    gevent.monkey.patch_item(to_patch, 'Empty', gevent.queue.Empty)
