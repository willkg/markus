===================
Testing with Markus
===================

.. contents::
   :local:


Asserting things about emitted metrics
======================================

Markus comes with a :py:class:`markus.testing.MetricsMock` that makes it easier
to write tests and assert things about generated metrics.

When activating the :py:class:`markus.testing.MetricsMock` context, it becomes
a backend for all emitted metrics. It'll capture metrics emitted. You can
assert things about the metrics collected.

There are a set of ``assert_*`` helper methods for simplifying that code, but
you can also use :py:meth:`markus.testing.MetricsMock.filter_records`
directly.


pytest plugin
=============

Markus includes a pytest plugin with a ``metricsmock`` pytest fixture. It's
implemented like this:

.. code-block::

   from markus.testing import MetricsMock

   import pytest

   @pytest.fixture
   def metricsmock() -> MetricsMock:
       with MetricsMock() as mm:
           yield mm


Testing against tag values
==========================

You can assert against tags ignoring the actual values using
:py:class:`markus.testing.AnyTagValue`.

.. code-block:: python

   from markus.testing import MetricsMock

   def test_something():
       with MetricsMock() as mm:
           # Do things that might record metrics here

           # Assert something about the metrics recorded
           mm.assert_incr(stat="some.random.key", value=1, tags=[AnyTagValue("host")])


Test module API
===============

.. automodule:: markus.testing
   :members:
