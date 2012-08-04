python-memcached-gmond
======================

This is a Python Gmond module for Memcached, compatible with both Python 2 and
3. In addition to the usual datapoints provided by "stats", this module
aggregates max age metrics from "stats items". All metrics are available in a
"memcached" collection group.

If you've installed ganglia at the standard locations, you should be able to
install this module by copying `memcached.pyconf` to `/etc/ganglia/conf.d` and
`memcached.py` & `memcached_metrics.py` to `/usr/lib/ganglia/python_modules`

For more information, including installation instructions, see the section
[Gmond Python metric modules][1] in the Ganglia documentation.

  [1]: http://sourceforge.net/apps/trac/ganglia/wiki/ganglia_gmond_python_modules
