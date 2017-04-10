# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time

from markus.backends.cloudwatch import CloudwatchMetrics


@freeze_time('2017-03-06 16:30:00', tz_offset=0)
class TestCloudwatch:
    def test_incr(self, capsys):
        ddcm = CloudwatchMetrics({})

        ddcm.incr('foo', value=10, tags=['key1:val', 'key2:val'])
        out, err = capsys.readouterr()
        assert out == 'MONITORING|1488817800|10|count|foo|#key1:val,key2:val\n'
        assert err == ''

    def test_gauge(self, capsys):
        ddcm = CloudwatchMetrics({})

        ddcm.gauge('foo', value=100, tags=['key1:val', 'key2:val'])
        out, err = capsys.readouterr()
        assert out == 'MONITORING|1488817800|100|gauge|foo|#key1:val,key2:val\n'
        assert err == ''

    def test_timing(self, capsys):
        # .timing is a gauge
        ddcm = CloudwatchMetrics({})

        ddcm.timing('foo', value=100, tags=['key1:val', 'key2:val'])
        out, err = capsys.readouterr()
        assert out == 'MONITORING|1488817800|100|gauge|foo|#key1:val,key2:val\n'
        assert err == ''

    def test_histogram(self, capsys):
        # .histogram is a gauge
        ddcm = CloudwatchMetrics({})

        ddcm.histogram('foo', value=100, tags=['key1:val', 'key2:val'])
        out, err = capsys.readouterr()
        assert out == 'MONITORING|1488817800|100|gauge|foo|#key1:val,key2:val\n'
        assert err == ''
