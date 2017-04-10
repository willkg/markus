# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time

from markus.backends.logging import LoggingMetrics


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
