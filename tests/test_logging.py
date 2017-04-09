# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus.backends.logging import LoggingMetrics


def test_incr(caplog):
    lm = LoggingMetrics({})

    lm.incr('foo', value=10, tags=['key1:val', 'key2:val'])

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS INCR: foo 10 key1:val,key2:val')
        ]
    )


def test_gauge(caplog):
    lm = LoggingMetrics({})

    lm.gauge('foo', value=100, tags=['key1:val', 'key2:val'])

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS GAUGE: foo 100 key1:val,key2:val')
        ]
    )


def test_timing(caplog):
    lm = LoggingMetrics({})

    lm.timing('foo', value=1234, tags=['key1:val', 'key2:val'])

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS TIMING: foo 1234 key1:val,key2:val')
        ]
    )


def test_histogram(caplog):
    lm = LoggingMetrics({})

    lm.histogram('foo', value=4321, tags=['key1:val', 'key2:val'])

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS HISTOGRAM: foo 4321 key1:val,key2:val')
        ]
    )
