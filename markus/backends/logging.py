# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import datetime
import logging
import statistics
import time

from markus.backends import BackendBase


class LoggingMetrics(BackendBase):
    """Metrics backend that publishes to Python logging.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.logging.LoggingMetrics',
            'options': {
                'logger_name': 'markus',
                'leader': 'METRICS',
            }
        }

    The :py:class:`markus.backends.logging.LoggingMetrics` backend generates
    logging messages in this format::

        leader|timestamp|metric_type|stat|value|#tags


    For example::

        METRICS|2017-03-06 11:30:00|histogram|foo|4321|#key1:val


    This will log at the ``logging.INFO`` level.

    Options:

    * ``logger_name``: the name for the logger

      Defaults to ``"markus"``.

    * ``leader``: string at the start of the metrics line

      This makes it easier to parse logs for metrics data--you look for the
      leader and everything after that is parseable data.

      Defaults to ``"METRICS"``.

    """

    def __init__(self, options=None, filters=None):
        options = options or {}
        self.filters = filters or []
        self.logger_name = options.get("logger_name", "markus")
        self.logger = logging.getLogger(self.logger_name)
        self.leader = options.get("leader", "METRICS")

    def emit(self, record):
        self.logger.info(
            "%(leader)s|%(timestamp)s|%(kind)s|%(stat)s|%(value)s|%(tags)s"
            % {
                "leader": self.leader,
                # FIXME(willkg): Make this utc?
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "kind": record.stat_type,
                "stat": record.key,
                "value": record.value,
                "tags": ("#%s" % ",".join(record.tags)) if record.tags else "",
            }
        )


class LoggingRollupMetrics(BackendBase):
    """Experimental logging backend for rolling up stats over a period.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.logging.LoggingRollupMetrics',
            'options': {
                'logger_name': 'markus',
                'leader': 'ROLLUP',
                'flush_interval': 10
            }
        }

    The :py:class:`markus.backends.logging.LoggingRollupMetrics` backend
    generates rollups every *flush_interval* of stats generated during that
    period.

    For incr stats, it shows count and rate.

    For gauge stats, it shows count, current value, min value, and max value
    for the period.

    For timing and histogram stats, it shows count, min, average, median, 95%,
    and max for the period.

    This will log at the ``logging.INFO`` level.

    Options:

    * ``logger_name``: the name for the logger

      Defaults to ``"markus"``.

    * ``leader``: string at the start of the metrics line

      This makes it easier to parse logs for metrics data--you look for the
      leader and everything after that is parseable data.

      Defaults to ``"ROLLUP"``.

    * ``flush_interval``: interval to generate rollup data

      :py:class:`markus.backends.logging.LoggingRollupMetrics` will spit out
      rollup data every ``flush_interval`` seconds.

      Defaults to ``10`` seconds.

    .. Note::

       This backend is experimental, probably has bugs, and may change over
       time.

    """

    def __init__(self, options=None, filters=None):
        options = options or {}
        self.filters = filters or []

        self.flush_interval = options.get("flush_interval", 10)
        self.logger_name = options.get("logger_name", "markus")
        self.leader = options.get("leader", "ROLLUP")

        self.logger = logging.getLogger(self.logger_name)

        # Next time to rollup in seconds since epoch
        self.next_rollup = time.time() + self.flush_interval

        # Map of key -> values list
        self.incr_stats = {}
        self.gauge_stats = {}
        self.histogram_stats = {}

    def rollup(self):
        """Roll up stats and log them."""
        now = time.time()
        if now < self.next_rollup:
            return

        self.next_rollup = now + self.flush_interval

        for key, values in sorted(self.incr_stats.items()):
            self.logger.info(
                "%s INCR %s: count:%d|rate:%d/%d",
                self.leader,
                key,
                len(values),
                sum(values),
                self.flush_interval,
            )
            self.incr_stats[key] = []

        for key, values in sorted(self.gauge_stats.items()):
            if values:
                self.logger.info(
                    "%s GAUGE %s: count:%d|current:%s|min:%s|max:%s",
                    self.leader,
                    key,
                    len(values),
                    values[-1],
                    min(values),
                    max(values),
                )
            else:
                self.logger.info("%s (gauge) %s: no data", self.leader, key)

            self.gauge_stats[key] = []

        for key, values in sorted(self.histogram_stats.items()):
            if values:
                self.logger.info(
                    (
                        "%s HISTOGRAM %s: "
                        "count:%d|min:%.2f|avg:%.2f|median:%.2f|ninety-five:%.2f|max:%.2f"
                    ),
                    self.leader,
                    key,
                    len(values),
                    min(values),
                    statistics.mean(values),
                    statistics.median(values),
                    values[int(len(values) * 95 / 100)],
                    max(values),
                )
            else:
                self.logger.info("%s (histogram) %s: no data", self.leader, key)

            self.histogram_stats[key] = []

    def emit(self, record):
        stat_type_to_list = {
            "incr": self.incr_stats,
            "gauge": self.gauge_stats,
            "timing": self.histogram_stats,
            "histogram": self.histogram_stats,
        }

        self.rollup()

        # FIXME(willkg): what to do with tags?
        stat_type_to_list[record.stat_type].setdefault(record.key, []).append(
            record.value
        )
