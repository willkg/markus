# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from markus.backends import BackendBase


class DatadogCloudwatchMetrics(BackendBase):
    """Publishes metrics to stdout for Datadog AWS Lambda support

    This prints to stdout in this format::

        MONITORING|unix_epoch_timestamp|value|metric_type|my.metric.name|#tag1:value,tag2

    That's the format that Datadog will be watching for in Cloudwatch.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.cloudwatch.DatadogCloudwatchMetrics',
        }

    This backend doesn't take any options.

    .. NOTE::

       Datadog doesn't support metrics other than incr (count) and gauge. This
       backend will send timing and histogram metrics as gauges.

    .. seealso::

       http://docs.datadoghq.com/integrations/awslambda/

       https://www.datadoghq.com/blog/monitoring-lambda-functions-datadog/#toc-beyond-standard-metrics

    """
    def _log(self, metrics_kind, stat, value, tags):
        print('MONITORING|%(timestamp)s|%(value)s|%(kind)s|%(stat)s|%(tags)s' % {
            'timestamp': int(time.time()),
            'kind': metrics_kind,
            'stat': stat,
            'value': value,
            'tags': ('#%s' % ','.join(tags)) if tags else ''
        })

    def incr(self, stat, value=1, tags=None):
        """Increment a counter"""
        self._log('count', stat, value, tags)

    def gauge(self, stat, value, tags=None):
        """Set a gauge"""
        self._log('gauge', stat, value, tags)

    def timing(self, stat, value, tags=None):
        """Does the same thing as gauge"""
        self._log('gauge', stat, value, tags)

    def histogram(self, stat, value, tags=None):
        """Does the same thing as gauge"""
        self._log('gauge', stat, value, tags)
