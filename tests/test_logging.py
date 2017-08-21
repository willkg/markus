# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time

from markus.backends.logging import LoggingMetrics, LoggingRollupMetrics


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
class TestLoggingMetrics:
    def test_incr(self, caplog):
        lm = LoggingMetrics({})

        lm.incr('foo', value=10, tags=['key1:val', 'key2:val'])

        assert (
            caplog.record_tuples ==
            [
                ('markus', 20, 'METRICS|2017-03-06 16:30:00|incr|foo|10|#key1:val,key2:val')
            ]
        )

    def test_gauge(self, caplog):
        lm = LoggingMetrics({})

        lm.gauge('foo', value=100, tags=['key1:val', 'key2:val'])

        assert (
            caplog.record_tuples ==
            [
                ('markus', 20, 'METRICS|2017-03-06 16:30:00|gauge|foo|100|#key1:val,key2:val')
            ]
        )

    def test_timing(self, caplog):
        lm = LoggingMetrics({})

        lm.timing('foo', value=1234, tags=['key1:val', 'key2:val'])

        assert (
            caplog.record_tuples ==
            [
                ('markus', 20, 'METRICS|2017-03-06 16:30:00|timing|foo|1234|#key1:val,key2:val')
            ]
        )

    def test_histogram(self, caplog):
        lm = LoggingMetrics({})

        lm.histogram('foo', value=4321, tags=['key1:val', 'key2:val'])

        assert (
            caplog.record_tuples ==
            [
                ('markus', 20, 'METRICS|2017-03-06 16:30:00|histogram|foo|4321|#key1:val,key2:val')
            ]
        )


class TestLoggingRollupMetrics:
    def test_rollup(self, caplog):
        with freeze_time('2017-04-19 12:00:00'):
            lm = LoggingRollupMetrics({})
            lm.incr('foo')
            lm.incr('foo')
            lm.gauge('widget', value=10)
            lm.incr('foo')
            lm.incr('bar')
            lm.gauge('widget', value=20)
            lm.gauge('widget', value=5)
            lm.histogram('save_time', value=50)
            lm.histogram('save_time', value=60)

        with freeze_time('2017-04-19 12:00:11'):
            lm.incr('bar')

        assert (
            caplog.record_tuples ==
            [
                ('markus', 20, 'ROLLUP INCR bar: count:1|rate:1/10'),
                ('markus', 20, 'ROLLUP INCR foo: count:3|rate:3/10'),
                ('markus', 20, 'ROLLUP GAUGE widget: count:3|current:5|min:5|max:20'),
                (
                    'markus', 20,
                    'ROLLUP HISTOGRAM save_time: '
                    'count:2|min:50.00|avg:55.00|median:55.00|ninety-five:60.00|max:60.00'
                )
            ]
        )
