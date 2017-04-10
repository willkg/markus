# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import datetime
import logging

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

    * logger_name: the name for the logger

      Defaults to ``"markus"``.

    * leader: string at the start of the metrics line

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
