# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time

from markus.backends.cloudwatch import DatadogCloudwatchMetrics


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
def test_incr(capsys):
    ddcm = DatadogCloudwatchMetrics({})

    ddcm.incr('foo', 10)
    out, err = capsys.readouterr()
    assert out == 'MONITORING|1488817800|10|count|foo|\n'
    assert err == ''


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
def test_gauge(capsys):
    ddcm = DatadogCloudwatchMetrics({})

    ddcm.gauge('foo', 100)
    out, err = capsys.readouterr()
    assert out == 'MONITORING|1488817800|100|gauge|foo|\n'
    assert err == ''


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
def test_timing(capsys):
    # .timing is a gauge
    ddcm = DatadogCloudwatchMetrics({})

    ddcm.timing('foo', 100)
    out, err = capsys.readouterr()
    assert out == 'MONITORING|1488817800|100|gauge|foo|\n'
    assert err == ''


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
def test_histogram(capsys):
    # .histogram is a gauge
    ddcm = DatadogCloudwatchMetrics({})

    ddcm.histogram('foo', 100)
    out, err = capsys.readouterr()
    assert out == 'MONITORING|1488817800|100|gauge|foo|\n'
    assert err == ''
