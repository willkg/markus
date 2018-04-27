History
=======

1.2.0 (April 27th, 2018)
------------------------

**Features**

* Add ``.clear()`` to ``MetricsMock`` making it easier to build a pytest
  fixture with the ``MetricsMock`` context and manipulate records for easy
  testing. #29

**Bug fix**

* Update Cloudwatch backend fixing ``.timing()`` and ``.histogram()`` to
  send ``histogram`` metrics type which Datadog now supports. #31


1.1.2 (April 5th, 2018)
-----------------------

**Typo fix**

* Fix the date from the previous release. Ugh.


1.1.1 (April 5th, 2018)
-----------------------

**Features**

* Official switch to semver.

**Bug fixes**

* Fix ``MetricsMock`` so it continues to work even if ``configure``
  is called. #27


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
