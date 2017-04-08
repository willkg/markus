=====
Usage
=====

Markus is used similar to Python's built-in logging library. To use Markus, you
need to do three things:

1. Configure Markus' backends using :py:func:`markus.configure`.

2. For each Python module or class or however you want to organize it, you use
   :py:func:`markus.get_metrics` to get a
   :py:class:`markus.main.MetricsInterface`.

3. Use the various metrics reporting methods on the
   :py:class:`markus.main.MetricsInterface`.


``markus.configure``
====================

.. autofunction:: markus.configure


``markus.get_metrics``
======================

.. autofunction:: markus.get_metrics


``markus.main.MetricsInterface``
================================

.. autoclass:: markus.main.MetricsInterface
   :members:
   :member-order: bysource
