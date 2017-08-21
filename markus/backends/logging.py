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
    """Metrics backend that publishes to Python logging

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
    def __init__(self, options):
        self.logger_name = options.get('logger_name', 'markus')
        self.logger = logging.getLogger(self.logger_name)
        self.leader = options.get('leader', 'METRICS')

    def _log(self, metrics_kind, stat, value, tags):
        self.logger.info(
            '%(leader)s|%(timestamp)s|%(kind)s|%(stat)s|%(value)s|%(tags)s' % {
                'leader': self.leader,
                # FIXME(willkg): Make this utc?
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'kind': metrics_kind,
                'stat': stat,
                'value': value,
                'tags': ('#%s' % ','.join(tags)) if tags else ''
            }
        )

    def incr(self, stat, value=1, tags=None):
        """Increment a counter"""
        self._log('incr', stat, value, tags)

    def gauge(self, stat, value, tags=None):
        """Set a gauge"""
        self._log('gauge', stat, value, tags)

    def timing(self, stat, value, tags=None):
        """Report a timing"""
        self._log('timing', stat, value, tags)

    def histogram(self, stat, value, tags=None):
        """Report a histogram"""
        self._log('histogram', stat, value, tags)


class LoggingRollupMetrics(BackendBase):
    """EXPERIMENTAL BACKEND FOR ROLLUPS

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

    """
    def __init__(self, options):
        self.flush_interval = options.get('flush_interval', 10)
        self.logger_name = options.get('logger_name', 'markus')
        self.leader = options.get('leader', 'ROLLUP')

        self.logger = logging.getLogger(self.logger_name)

        # Next time to rollup in seconds since epoch
        self.next_rollup = time.time() + self.flush_interval

        # Map of key -> values list
        self.incr_stats = {}
        self.gauge_stats = {}
        self.histogram_stats = {}

    def rollup(self):
        now = time.time()
        if now < self.next_rollup:
            return

        self.next_rollup = now + self.flush_interval

        for key, values in sorted(self.incr_stats.items()):
            self.logger.info(
                '%s INCR %s: count:%d|rate:%d/%d',
                self.leader,
                key,
                len(values),
                sum(values),
                self.flush_interval
            )
            self.incr_stats[key] = []

        for key, values in sorted(self.gauge_stats.items()):
            if values:
                self.logger.info(
                    '%s GAUGE %s: count:%d|current:%s|min:%s|max:%s',
                    self.leader,
                    key,
                    len(values),
                    values[-1],
                    min(values),
                    max(values),
                )
            else:
                self.logger.info('%s (gauge) %s: no data', self.leader, key)

            self.gauge_stats[key] = []

        for key, values in sorted(self.histogram_stats.items()):
            if values:
                self.logger.info(
                    (
                        '%s HISTOGRAM %s: '
                        'count:%d|min:%.2f|avg:%.2f|median:%.2f|ninety-five:%.2f|max:%.2f'
                    ),
                    self.leader,
                    key,
                    len(values),
                    min(values),
                    statistics.mean(values),
                    statistics.median(values),
                    values[int(len(values) * 95 / 100)],
                    max(values)
                )
            else:
                self.logger.info('%s (histogram) %s: no data', self.leader, key)

            self.histogram_stats[key] = []

    def incr(self, stat, value=1, tags=None):
        self.rollup()

        # FIXME(willkg): what to do with tags?
        self.incr_stats.setdefault(stat, []).append(value)

    def gauge(self, stat, value, tags=None):
        self.rollup()

        # FIXME(willkg): what to do with tags?
        self.gauge_stats.setdefault(stat, []).append(value)

    def timing(self, stat, value, tags=None):
        # timing is a special case for histogram
        self.histogram(stat, value, tags)

    def histogram(self, stat, value, tags=None):
        self.rollup()

        # FIXME(willkg): what to do with tags?
        self.histogram_stats.setdefault(stat, []).append(value)
