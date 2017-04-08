# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import logging

from markus.backends import BackendBase


class LoggingMetrics(BackendBase):
    """Metrics backend that logs the values.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.logging.LoggingMetrics',
            'options': {
                'logger_name': 'metrics',
                'msg_prefix': 'METRICS',
            }
        }


    Options:

    * logger_name: the name for the logger

      Defaults to ``"metrics"``.

    * msg_prefix: any prefix to spit out before the metrics data

      Defaults to ``"METRICS"``.

    """
    def __init__(self, options):
        self.logger = logging.getLogger(options.get('logger_name', 'metrics'))
        self.msg_prefix = options.get('msg_prefix', 'METRICS')

    def _log(self, metrics_kind, stat, kwargs):
        self.logger.info(
            '%s %s: %s %s', self.msg_prefix, metrics_kind, stat, kwargs
        )

    def incr(self, stat, **kwargs):
        """Increment a counter"""
        self._log('INCR', stat, kwargs)

    def gauge(self, stat, **kwargs):
        """Set a gauge"""
        self._log('GAUGE', stat, kwargs)

    def timing(self, stat, **kwargs):
        """Report a timing"""
        self._log('TIMING', stat, kwargs)

    def histogram(self, stat, **kwargs):
        """Report a histogram"""
        self._log('HISTOGRAM', stat, kwargs)
