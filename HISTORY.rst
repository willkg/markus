History
=======

4.1.0 (November 7th, 2022)
--------------------------

**Features**

* Add support for Python 3.11 (#100)

**Bug fixes**

* Redo how dev environment works so it's no longer installed via an extras but
  is now in a separate requirements-dev.txt file.

* Split flake8 tou a separate requirements-flake8.txt and tox environment to
  handle conflicts with installing other things.


4.0.1 (May 10th, 2022)
----------------------

**Bug fixes**

* Move pytest import to a pytest plugin so it's easier to determine when pytest
  is running. (#95) Thank you, John!


4.0.0 (October 22nd, 2021)
--------------------------

**Features**

* Added support for Python 3.10 (#88)

**Backwards incompatibel changes**

* Dropped support for Python 3.6 (#89)


3.0.0 (February 5th, 2021)
--------------------------

**Features**

* Added support for Python 3.9 (#79). Thank you, Brady!

* Changed ``assert_*`` helper methods on ``markus.testing.MetricsMock``
  to print the records to stdout if the assertion fails. This can save some
  time debugging failing tests. (#74)

**Backwards incompatible changes**

* Dropped support for Python 3.5 (#78). Thank you, Brady!

* ``markus.testing.MetricsMock.get_records`` and
  ``markus.testing.MetricsMock.filter_records`` return
  ``markus.main.MetricsRecord`` instances now. This might require
  you to rewrite/update tests that use the ``MetricsMock``.


2.2.0 (April 15th, 2020)
------------------------

**Features**

* Add ``assert_`` methods to ``MetricsMock`` to reduce the boilerplate for
  testing. Thank you, John! (#68)

**Bug fixes**

* Remove use of ``six`` library. (#69)


2.1.0 (October 7th, 2019)
-------------------------

**Features**

* Fix ``get_metrics()`` so you can call it without passing in a `thing`
  and it'll now create a ``MetricsInterface`` that doesn't have a key
  prefix. (#59)


2.0.0 (September 19th, 2019)
----------------------------

**Features**

* Use ``time.perf_counter()`` if available. Thank you, Mike! (#34)
* Support Python 3.7 officially.
* Add filters for adjusting and dropping metrics getting emitted.
  See documentation for more details. (#40)

**Backwards incompatible changes**

* ``tags`` now defaults to ``[]`` instead of ``None`` which may affect some
  expected test output.
* Adjust internals to run ``.emit()`` on backends. If you wrote your own
  backend, you may need to adjust it.
* Drop support for Python 3.4. (#39)
* Drop support for Python 2.7.
  
  If you're still using Python 2.7, you'll need to pin to ``<2.0.0``. (#42)

**Bug fixes**

* Document feature support in backends. (#47)
* Fix ``MetricsMock.has_record()`` example. Thank you, John!


1.2.0 (April 27th, 2018)
------------------------

**Features**

* Add ``.clear()`` to ``MetricsMock`` making it easier to build a pytest
  fixture with the ``MetricsMock`` context and manipulate records for easy
  testing. (#29)

**Bug fixes**

* Update Cloudwatch backend fixing ``.timing()`` and ``.histogram()`` to
  send ``histogram`` metrics type which Datadog now supports. (#31)


1.1.2 (April 5th, 2018)
-----------------------

**Typo fixes**

* Fix the date from the previous release. Ugh.


1.1.1 (April 5th, 2018)
-----------------------

**Features**

* Official switch to semver.

**Bug fixes**

* Fix ``MetricsMock`` so it continues to work even if ``configure``
  is called. (#27)


1.1 (November 13th, 2017)
-------------------------

**Features**

* Added ``markus.utils.generate_tag`` utility function


1.0 (October 30th, 2017)
------------------------

**Features**

* Added support for Python 2.7.

* Added a ``markus.backends.statsd.StatsdMetrics`` backend that uses
  pystatsd client for statsd pings. Thank you, Javier!

**Bug fixes**

* Added ``LoggingRollupMetrics`` to docs.

* Mozilla has been running Markus in production for 6 months so we
  can mark it production-ready now.


0.2 (April 19th, 2017)
----------------------

**Features**

* Added a ``markus.backends.logging.LoggingRollupMetrics`` backend that
  rolls up metrics and does some light math on them. Possibly helpful
  for light profiling for development.

**Bug fixes**

* Lots of documentation fixes. Thank you, Peter!


0.1 (April 10th, 2017)
----------------------

Initial writing.
