# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from markus.backends import BackendBase


class DatadogCloudwatchMetrics(BackendBase):
    """Publishes metrics to stdout for Datadog AWS Lambda support

    http://docs.datadoghq.com/integrations/awslambda/

    https://www.datadoghq.com/blog/monitoring-lambda-functions-datadog/#toc-beyond-standard-metrics  # noqa

    To use, add this to your backends list::

        {
            'class': 'markus.backends.cloudwatch.DatadogCloudwatchMetrics',
        }

    This doesn't take any options.

    .. NOTE::

       Datadog doesn'ts upport metrics other than incr (count) and gauge. Using
       timing and histogram will send those values as a gauge.

    """
    def _log(self, metrics_kind, stat, value):
        print('MONITORING|%(timestamp)s|%(value)s|%(kind)s|%(stat)s|' % {
            'timestamp': int(time.time()),
            'kind': metrics_kind,
            'stat': stat,
            'value': value,
        })

    def incr(self, stat, value=1):
        self._log('count', stat, value)

    def gauge(self, stat, value):
        self._log('gauge', stat, value)

    timing = gauge
    histogram = gauge
