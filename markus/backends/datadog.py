# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import logging

from datadog.dogstatsd import DogStatsd
from markus.backends import BackendBase


logger = logging.getLogger(__name__)


class DatadogMetrics(BackendBase):
    """Uses the Datadog DogStatsd client for statsd pings.

    This requires the Datadog backend and requirements be installed.
    To install those bits, do::

        $ pip install markus[datadog]


    To use, add this to your backends list::

        {
            'class': 'markus.backends.datadog.DatadogMetrics',
            'options': {
                'statsd_host': 'localhost',
                'statsd_port': 8125,
                'statsd_namespace': '',
            }
        }


    Options:

    * statsd_host: the hostname for the statsd daemon to connect to

      Defaults to ``"localhost"``.

    * statsd_port: the port for the statsd daemon to connect to

      Defaults to ``8125``.

    * statsd_namespace: the namespace to use for statsd data

      Defaults to ``''``.


    .. seealso::

       http://docs.datadoghq.com/guides/metrics/

    """
    def __init__(self, options):
        self.host = options.get('statsd_host', 'localhost')
        self.port = options.get('statsd_port', 8125)
        self.namespace = options.get('statsd_namespace', '')

        self.client = self.get_client(self.host, self.port, self.namespace)
        logger.info(
            '%s configured: %s:%s %s',
            self.__class__.__name__, self.host, self.port, self.namespace
        )

    def get_client(self, host, port, namespace):
        return DogStatsd(host=host, port=port, namespace=namespace)

    def incr(self, stat, value=1, tags=None):
        """Increment a counter"""
        self.client.increment(metric=stat, value=value, tags=tags)

    def gauge(self, stat, value, tags=None):
        """Set a gauge"""
        self.client.gauge(metric=stat, value=value, tags=tags)

    def timing(self, stat, value, tags=None):
        """Measure a timing for statistical distribution"""
        self.client.timing(metric=stat, value=value, tags=tags)

    def histogram(self, stat, value, tags=None):
        """Measure a value for statistical distribution"""
        self.client.histogram(metric=stat, value=value, tags=tags)
