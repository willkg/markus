# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import logging

from statsd import StatsClient
from markus.backends import BackendBase


logger = logging.getLogger(__name__)


class StatsdMetrics(BackendBase):
    """Use pystatsd client for statsd pings.

    This requires the pystatsd module and requirements to be installed.
    To install those bits, do::

        $ pip install markus[statsd]


    To use, add this to your backends list::

        {
            'class': 'markus.backends.statsd.StatsdMetrics',
            'options': {
                'statsd_host': 'statsd.example.com',
                'statsd_port': 8125,
                'statsd_prefix': None,
                'statsd_maxudpsize': 512,
            }
        }


    Options:

    * statsd_host: the hostname for the statsd daemon to connect to

      Defaults to ``'localhost'``.

    * statsd_port: the port for the statsd daemon to connect to

      Defaults to ``8125``.

    * statsd_prefix: the prefix to use for statsd data

      Defaults to ``None``.

    * statsd_maxudpsize: the maximum data to send per packet

      Defaults to ``512``.

    .. Note::

       The StatsdMetrics backend does not support tags. All tags will
       be dropped when metrics are emitted by this backend.

    .. Note::

       statsd doesn't support histograms so histogram metrics are
       reported as timing metrics.

    .. seealso::

       https://statsd.readthedocs.io/en/latest/configure.html

    """

    def __init__(self, options=None, filters=None):
        options = options or {}
        self.host = options.get("statsd_host", "localhost")
        self.port = options.get("statsd_port", 8125)
        self.prefix = options.get("statsd_prefix")
        self.maxudpsize = options.get("statsd_maxudpsize", 512)

        self.filters = filters or []

        self.client = self._get_client(
            self.host, self.port, self.prefix, self.maxudpsize
        )
        logger.info(
            "%s configured: %s:%s %s",
            self.__class__.__name__,
            self.host,
            self.port,
            self.prefix,
        )

    def _get_client(self, host, port, prefix, maxudpsize):
        return StatsClient(host=host, port=port, prefix=prefix, maxudpsize=maxudpsize)

    def emit(self, record):
        stat_type = record.stat_type
        if stat_type == "incr":
            self.client.incr(stat=record.key, count=record.value)
        elif stat_type == "gauge":
            self.client.gauge(stat=record.key, value=record.value)
        elif stat_type in ("timing", "histogram"):
            self.client.timing(stat=record.key, delta=record.value)
