=======
Filters
=======

Markus lets you write and use filters to modify generated metrics.


Using filters
=============

Filters can be configured to run on a ``MetricsInterface`` instance
that you build with ``get_metrics()``.

For example, say you had a Python module and all metrics published from code
in that module should get the additional tag ``source:foomodule``. Then you
could do something like this::

    import markus
    from markus.main import MetricsFilter


    class SourceFilter(MetricsFilter):
        def __init__(self, sourcename):
            self.sourcename_tag = "source:%s" % sourcename

        def filter(self, record):
            record.tags.append(self.sourcename_tag)
            return record


    metrics = markus.get_metrics(__name__, filters=[SourceFilter("cache")])


    class CacheInterface:
        def get(self, key, default=None):
            with metrics.timing("cache.get"):
                # do stuff


The ``cache.get`` metric will have ``source:cache`` as a tag.

You can also specify filters on backends when configuring markus. For example,
say you want to add a ``hostid:HOSTID`` tag to all metrics being published to
the Datadog backend. You could do this::

    import os

    import markus
    from markus.main import MetricsFilter


    class HostFilter(MetricsFilter):
        def __init__(self, hostid):
            self.hostid_tag = "hostid:%s" % hostid

        def filter(self, record):
            record.tags.append(self.hostid_tag)
            return record


    HOSTID = os.environ.get("HOSTID", "none")

    markus.configure(
        backends=[
            {
                "class": "markus.backends.datadog.DatadogMetrics",
                "options": {
                    "statsd_host": "example.com",
                    "statsd_port": 8125,
                    "statsd_namespace": ""
                },
                "filters": [HostFilter(HOSTID)]
            }
        ]
    )

All metrics generated will have the ``hostid`` tag.

Filters can be used to drop metrics, too. Say you want metrics with
``debug:true`` spit out to the logging backend, but not the Datadog backend.
You could do this::

    import os

    import markus
    from markus.main import MetricsFilter


    class DropDebugFilter(MetricsFilter):
        def filter(self, record):
            if "debug:true" in record.tags:
                return
            return record

    markus.configure(
        backends=[
            {
                "class": "markus.backends.datadog.DatadogMetrics",
                "options": {
                    "statsd_host": "example.com",
                    "statsd_port": 8125,
                    "statsd_namespace": ""
                },
                "filters": [DropDebugFilter()]
            },
            {
                # Log metrics to the logs
                'class': 'markus.backends.logging.LoggingMetrics',
            },
        ]
    )

Metrics generated with ``debug:true`` will show up in the logs, but not get
sent to the Datadog backend.


Writing filters
===============

Filters subclass the ``markus.main.MetricsFilter`` class.

All filters need to implement the ``.filter()`` method.

This filter adds a host id tag to all outgoing metrics::

    import os

    from markus.main import MetricsFilter


    class HostFilter(MetricsFilter):
        def __init__(self):
            self.hostid_tag = "hostid:%s" % os.environ.get("HOSTID")

        def filter(self, record):
            record.tags.append(self.hostid_tag)
            return record

Filters can also drop metrics. This one drops any metric that has a
"debug:true" tag::

    from markus.main import

    class DebugFilter(MetricsFilter):
        def filter(self, record):
            if "debug:true" in record.tags:
                return
            return record



