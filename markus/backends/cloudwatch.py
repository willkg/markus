# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from markus.backends import BackendBase


class CloudwatchMetrics(BackendBase):
    """Publish metrics to stdout for Cloudwatch.

    This prints to stdout in this format::

        MONITORING|unix_epoch_timestamp|value|metric_type|my.metric.name|#tag1:value,tag2

    It lets you generate metrics for reading/consuming in Cloudwatch.

    For example, Datadog can consume metrics formatted this way from Cloudwatch
    allowing you to generate metrics in AWS Lambda functions and have them show
    up in Datadog.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.cloudwatch.CloudwatchMetrics',
        }

    This backend doesn't take any options.

    .. Note::

       Datadog's Cloudwatch through Lambda logs supports four metrics types:
       count, gauge, histogram, and check. Thus all timing metrics are treated
       as histogram metrics.

    .. seealso::

       https://docs.datadoghq.com/integrations/amazon_lambda/

       https://docs.datadoghq.com/developers/metrics/#metric-names

    """

    def emit(self, record):
        stat_type_to_kind = {
            "incr": "count",
            "gauge": "gauge",
            "timing": "histogram",
            "histogram": "histogram",
        }
        print(
            "MONITORING|%(timestamp)s|%(value)s|%(kind)s|%(stat)s|%(tags)s"
            % {
                "timestamp": int(time.time()),
                "kind": stat_type_to_kind[record.stat_type],
                "stat": record.key,
                "value": record.value,
                "tags": ("#%s" % ",".join(record.tags)) if record.tags else "",
            }
        )
