========
Backends
========

Markus comes with several backends. You can also write your own.


Logging metrics
===============

.. autoclass:: markus.backends.logging.LoggingMetrics
   :members:
   :special-members:


.. autoclass:: markus.backends.logging.LoggingRollupMetrics
   :members:
   :special-members:


Statsd metrics
===============

.. autoclass:: markus.backends.statsd.StatsdMetrics
   :members:
   :special-members:


Datadog metrics
===============

.. autoclass:: markus.backends.datadog.DatadogMetrics
   :members:
   :special-members:


Cloudwatch metrics
==================

.. autoclass:: markus.backends.cloudwatch.CloudwatchMetrics
   :members:
   :special-members:


Writing your own
================

1. Subclass ``markus.backends.BackendBase``.

2. Implement ``__init__``. It takes a single "options" dict with stuff the
   user configured.

3. Implement ``incr``, ``gauge``, ``timing``, and ``histogram`` and have them
   do whatever is appropriate in the context of your backend.


.. autoclass:: markus.backends.BackendBase
   :members: __init__, incr, gauge, timing, histogram


For example, here's a backend that prints metrics to stdout:

.. doctest::

    >>> import markus
    >>> from markus.backends import BackendBase

    >>> class StdoutMetrics(BackendBase):
    ...     def __init__(self, options):
    ...         self.prefix = options.get('prefix', '')
    ...
    ...     def _generate(self, kind, stat, value, tags, **extras):
    ...         print('%s %s %s %s tags=%s %s' % (kind, self.prefix, stat, value, tags, extras))
    ...
    ...     def incr(self, stat, value, tags=None):
    ...         self._generate('incr', stat, value, tags)
    ...
    ...     def gauge(self, stat, value, tags=None):
    ...         self._generate('gauge', stat, value, tags)
    ...
    ...     def timing(self, stat, value, tags=None):
    ...         self._generate('timing', stat, value, tags)
    ...
    ...     def histogram(self, stat, value, tags=None):
    ...         self._generate('histogram', stat, value, tags)
    ...
    >>> markus.configure([{'class': StdoutMetrics, 'options': {'prefix': 'foo'}}], raise_errors=True)

    >>> metrics = markus.get_metrics('test')
    >>> metrics.incr('key1', value=1)
    incr foo test.key1 1 tags=None {}


.. testcleanup:: *

   import markus
   markus.configure([])


This will print to stdout ``foo incr test.key1 1 None {}``.
