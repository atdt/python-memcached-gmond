#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Python Gmond Module for Memcached

    This module declares a "memcached" collection group. For more information,
    including installation instructions, see:

    http://sourceforge.net/apps/trac/ganglia/wiki/ganglia_gmond_python_modules

    When invoked as a standalone script, this module will attempt to use the
    default configuration to query memcached every 5 seconds and print out the
    results.

    Based on a suggestion from Domas Mitzuas, this module also reports the min,
    max, median and mean of the 'age' metric across slabs, as reported by the
    "stats items" memcached command.

    :copyright: (c) 2012 Wikimedia Foundation
    :author: Ori Livneh <ori@wikimedia.org>
    :license: GPL
"""
from __future__ import division, print_function

import json
import telnetlib

# Default configuration
config = {
    'host' : '127.0.0.1',
    'port' : 11211,
    'defs' : './memcached-metrics.json'
}


stats = {}
client = telnetlib.Telnet()


def median(values):
    """Calculate median of series"""
    values = sorted(values)
    length = len(values)
    mid = length // 2
    if (length % 2):
        return values[mid]
    else:
        return (values[mid - 1] + values[mid]) / 2


def mean(values):
    """Calculate mean (average) of series"""
    return sum(values) / len(values)


def cast(value):
    """Cast value to float or int, if possible"""
    try:
        return float(value) if '.' in value else int(value)
    except ValueError:
        return value


def query(command):
    """Send `command` to memcached and stream response"""
    client.write(command.encode('ascii') + b'\n')
    while True:
        line = client.read_until(b'\r\n').decode('ascii').strip()
        if not line or line == 'END':
            break
        (_, metric, value) = line.split(None, 2)
        yield metric, cast(value)


def update_stats():
    """Refresh stats by polling memcached server"""
    try:
        client.open(**config)
        stats.update(query('stats'))
        ages = [v for k, v in query('stats items') if k.endswith('age')]
        if not ages:
            return {'age_min': 0, 'age_max': 0, 'age_mean': 0, 'age_median': 0}
        stats.update({
            'age_min'    : min(ages),
            'age_max'    : max(ages),
            'age_mean'   : mean(ages),
            'age_median' : median(ages)
        })
    finally:
        client.close()


## Gmond interface (metric_init, metric_handler, metric_close)


def metric_init(params):
    """Initialize; part of Gmond interface"""
    print('[memcached] memcached stats')
    config.update(params)
    with open(config.pop('defs'), 'rt') as f:
        descriptors = json.load(f)
    for metric in descriptors:
        metric['call_back'] = metric_handler
    return descriptors


def metric_handler(name):
    """
    Get the value for a particular metric. Asking for a metric twice triggers
    an update. This ensures memcached is queried once per gmond poll. This
    function is specified as the 'call_back' for each metric descriptor. Part
    of Gmond interface.
    """
    value = stats.pop(name, None)
    if value is None:
        update_stats()
        return stats[name]
    return value


def metric_cleanup():
    """Teardown; part of Gmond interface"""
    client.close()


if __name__ == '__main__':
    # When invoked as standalone script, run a self-test by querying each
    # metric descriptor and printing it out.
    from time import sleep

    print("Polling 127.0.0.1:11211 with a 5 second interval:\n")
    params = config.copy()
    while True:
        for metric in metric_init(params):
            value = metric['call_back'](metric['name'])
            print(( "%s => " + metric['format'] ) % ( metric['name'], value ))
        print('')
        sleep(5)
