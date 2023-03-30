# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import logging

from datadog.dogstatsd import DogStatsd
from markus.backends import BackendBase


logger = logging.getLogger(__name__)


class DatadogMetrics(BackendBase):
    """Use the Datadog DogStatsd client for statsd pings.

    This requires the Datadog backend and requirements be installed.
    To install those bits, do::

        $ pip install markus[datadog]


    To use, add this to your backends list::

        {
            "class": "markus.backends.datadog.DatadogMetrics",
            "options": {
                "statsd_host": "localhost",
                "statsd_port": 8125,
                "statsd_namespace": "",
            }
        }


    Options:

    * statsd_host: the hostname for the statsd daemon to connect to

      Defaults to ``"localhost"``.

    * statsd_port: the port for the statsd daemon to connect to

      Defaults to ``8125``.

    * statsd_namespace: the namespace to use for statsd data

      Defaults to ``""``.

    * origin_detection_enabled: whether or not the client should fill the
      container field (part of datadog protocol v1.2).

      Defaults to ``False``.

    .. seealso::

       https://docs.datadoghq.com/developers/metrics/

    """

    def __init__(self, options=None, filters=None):
        options = options or {}
        self.filters = filters or []

        self.host = options.get("statsd_host", "localhost")
        self.port = options.get("statsd_port", 8125)
        self.namespace = options.get("statsd_namespace", "")
        self.origin_detection_enabled = options.get("origin_detection_enabled", False)

        self.client = self._get_client(
            host=self.host,
            port=self.port,
            namespace=self.namespace,
            origin_detection_enabled=self.origin_detection_enabled,
        )
        logger.debug(
            "%s configured: %s:%s %s %s",
            self.__class__.__name__,
            self.host,
            self.port,
            self.namespace,
            self.origin_detection_enabled,
        )

    def _get_client(self, host, port, namespace, origin_detection_enabled):
        return DogStatsd(
            host=host,
            port=port,
            namespace=namespace,
            origin_detection_enabled=origin_detection_enabled,
        )

    def emit(self, record):
        stat_type_to_fun = {
            "incr": self.client.increment,
            "gauge": self.client.gauge,
            "timing": self.client.timing,
            "histogram": self.client.histogram,
        }
        metrics_fun = stat_type_to_fun[record.stat_type]
        metrics_fun(metric=record.key, value=record.value, tags=record.tags)
