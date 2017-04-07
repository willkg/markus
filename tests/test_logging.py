# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus.backends.logging import LoggingMetrics


def test_incr(caplog):
    lm = LoggingMetrics({})

    lm.incr('foo', value=10)

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS INCR: foo {\'value\': 10}')
        ]
    )


def test_gauge(caplog):
    lm = LoggingMetrics({})

    lm.gauge('foo', value=100)

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS GAUGE: foo {\'value\': 100}')
        ]
    )


def test_timing(caplog):
    lm = LoggingMetrics({})

    lm.timing('foo', value=1234)

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS TIMING: foo {\'value\': 1234}')
        ]
    )


def test_histogram(caplog):
    lm = LoggingMetrics({})

    lm.histogram('foo', value=4321)

    assert (
        caplog.record_tuples ==
        [
            ('metrics', 20, 'METRICS HISTOGRAM: foo {\'value\': 4321}')
        ]
    )
