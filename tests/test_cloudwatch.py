# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time

from markus.backends.cloudwatch import CloudwatchMetrics
from markus.main import MetricsFilter, MetricsRecord


@freeze_time("2017-03-06 16:30:00", tz_offset=0)
class TestCloudwatch:
    def test_incr(self, capsys):
        rec = MetricsRecord("incr", key="foo", value=10, tags=["key1:val", "key2:val"])
        ddcm = CloudwatchMetrics()
        ddcm.emit_to_backend(rec)
        out, err = capsys.readouterr()
        assert out == "MONITORING|1488817800|10|count|foo|#key1:val,key2:val\n"
        assert err == ""

    def test_gauge(self, capsys):
        rec = MetricsRecord(
            "gauge", key="foo", value=100, tags=["key1:val", "key2:val"]
        )
        ddcm = CloudwatchMetrics()
        ddcm.emit_to_backend(rec)
        out, err = capsys.readouterr()
        assert out == "MONITORING|1488817800|100|gauge|foo|#key1:val,key2:val\n"
        assert err == ""

    def test_timing(self, capsys):
        # .timing is a histogram
        rec = MetricsRecord(
            "timing", key="foo", value=100, tags=["key1:val", "key2:val"]
        )
        ddcm = CloudwatchMetrics()
        ddcm.emit_to_backend(rec)
        out, err = capsys.readouterr()
        assert out == "MONITORING|1488817800|100|histogram|foo|#key1:val,key2:val\n"
        assert err == ""

    def test_histogram(self, capsys):
        rec = MetricsRecord(
            "histogram", key="foo", value=100, tags=["key1:val", "key2:val"]
        )
        ddcm = CloudwatchMetrics()
        ddcm.emit_to_backend(rec)
        out, err = capsys.readouterr()
        assert out == "MONITORING|1488817800|100|histogram|foo|#key1:val,key2:val\n"
        assert err == ""

    def test_filters(self, capsys):
        class BlueFilter(MetricsFilter):
            def filter(self, record):
                if "blue" not in record.key:
                    return
                return record

        ddcm = CloudwatchMetrics(filters=[BlueFilter()])
        ddcm.emit_to_backend(MetricsRecord("incr", key="foo", value=1, tags=[]))
        ddcm.emit_to_backend(MetricsRecord("incr", key="foo.blue", value=2, tags=[]))
        out, err = capsys.readouterr()
        assert out == "MONITORING|1488817800|2|count|foo.blue|\n"
        assert err == ""
