#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Every

    Python decorator; decorated function is called on a set interval.

    :author: Ori Livneh <ori@wikimedia.org>
    :copyright: (c) 2012 Wikimedia Foundation
    :license: GPL, version 2 or later
"""
from datetime import timedelta
import signal
import sys
import threading


# pylint: disable=C0111, W0212, W0613, W0621


__all__ = ('every', )


def handle_sigint(signal, frame):
    """
    Attempt to kill all child threads and exit. Installing this as a sigint
    handler allows the program to run indefinitely if unmolested, but still
    terminate gracefully on Ctrl-C.
    """
    for thread in threading.enumerate():
        if thread.isAlive():
            thread._Thread__stop()
    sys.exit(0)


def every(*args, **kwargs):
    """
    Decorator; calls decorated function on a set interval. Arguments to every()
    are passed on to the constructor of datetime.timedelta(), which accepts the
    following arguments: days, seconds, microseconds, milliseconds, minutes,
    hours, weeks. This decorator is intended for functions with side effects;
    the return value is discarded.
    """
    interval = timedelta(*args, **kwargs).total_seconds()
    def decorator(func):
        def poll():
            func()
            threading.Timer(interval, poll).start()
        poll()
        return func
    return decorator


def join():
    """Pause until sigint"""
    signal.signal(signal.SIGINT, handle_sigint)
    signal.pause()


every.join = join
