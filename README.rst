======
Markus
======

Markus is a metrics generation library for generating statistics about your app.

:Code:          https://github.com/willkg/markus
:Issues:        https://github.com/willkg/markus/issues
:License:       MPL v2
:Documentation: TBD
:Status:        Alpha


Goals
=====

This library is structured similarly to the Python logging library and provides
an easy-to-use API for generating metrics across your application.


Install
=======

FIXME(willkg): This doesn't work, yet.

Run::

    $ pip install markus


To install Datadog StatsD backend::

    $ pip install markus[datadog]


Quick start
===========

Similar to using the logging library, every Python module can create a
``MetricsInterface`` (loosely equivalent to a Python logging logger) at any time
and use that to post metrics.

For example::

    import markus

    metrics = markus.get_metrics(__name__)


Then you can use it anywhere in that module::

    @metrics.timer_decorator('chopping_vegetables')
    def some_long_function(vegetable):
        for veg in vegetable:
            chop_vegetable()
            metrics.incr('vegetable', 1)


At application startup, you configure Markus with the backend you want and other
options.

For example, lets configure metrics to publish to logs and a StatsD host::

    import markus

    markus.configure(
        backends=[
            {
                # Log metrics to the logs
                'class': 'markus.backend.LoggingBackend',
            },
            {
                # Log metrics to StatsD
                'class': 'markus_statsd.backend.StatsDBackend',
                'options': {
                    'host': 'example.com',
                    'port': 8125,
                    'namespace': ''
                }
            }
        ]
    )


Markus comes with a MetricsMock to make testing easier, too::

    import markus
    from markus.testing import MetricsMock


    def test_something():
        with MetricsMock() as mm:
            # ... Do things that might publish metrics

            # This helps you debug and write your test
            mm.print_metrics()

            # Make assertions on metrics published
            assert mm.has_metric(markus.INCR, 'some.key', {'value': 1})
