===================
Testing with Markus
===================

Markus comes with a :py:class:`markus.testing.MetricsMock` that makes it easier
to write tests and assert things about generated metrics.

When activating the :py:class:`markus.testing.MetricsMock` context, it becomes
a backend for all emitted metrics. It'll contains a list of metrics emitted.
You can assert things about the metrics collected.

There are a set of ``assert_*`` helper methods for simplifying that code, but
you can also use :py:meth:`markus.testing.MetricsMock.filter_records`
directly.


.. autoclass:: markus.testing.MetricsMock
   :members:
