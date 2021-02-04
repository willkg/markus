========
Backends
========

Markus comes with several backends. You can also write your own.

.. contents::
   :local:


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

3. Implement ``emit`` and have it do whatever is appropriate in the context of
   your backend.


.. autoclass:: markus.backends.BackendBase
   :members: __init__, emit


The records that get emitted are :py:class:`markus.main.MetricsRecord` instances.


Here's an example backend that prints metrics to stdout:

.. doctest::

    >>> import markus
    >>> from markus.backends import BackendBase
    >>> from markus.main import MetricsRecord

    >>> class StdoutMetrics(BackendBase):
    ...     def __init__(self, options=None, filters=None):
    ...         options = options or {}
    ...         self.filters = filters or []
    ...         self.prefix = options.get('prefix', '')
    ...
    ...     def emit(self, record):
    ...         print('%s %s %s %s tags=%s' % (
    ...             record.stat_type,
    ...             self.prefix,
    ...             record.key,
    ...             record.value,
    ...             record.tags
    ...         ))
    ...
    >>> markus.configure([{'class': StdoutMetrics, 'options': {'prefix': 'foo'}}], raise_errors=True)

    >>> metrics = markus.get_metrics('test')
    >>> metrics.incr('key1')
    incr foo test.key1 1 tags=[]


.. testcleanup:: *

   import markus
   markus.configure([])
