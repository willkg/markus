========
Backends
========

Markus comes with several backends. You can also write your own.


Logging metrics
===============

.. autoclass:: markus.backends.logging.LoggingMetrics
   :members:
   :special-members:


Datadog metrics
===============

.. autoclass:: markus.backends.datadog.DatadogMetrics
   :members:
   :special-members:


Datadog Cloudwatch metrics
==========================

.. autoclass:: markus.backends.cloudwatch.DatadogCloudwatchMetrics
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
