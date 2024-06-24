# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import markus
from markus.testing import AnyTagValue, MetricsMock

import pytest


class TestAnyTagValue:
    def test_equality(self):
        # values are equal even if instances aren't
        assert AnyTagValue("host") == AnyTagValue("host")

        # equal to "host:" with any value
        assert AnyTagValue("host") == "host:1234"
        assert AnyTagValue("host") == "host:5678"
        assert AnyTagValue("host") == "host"

        # not equal to a different tag
        assert AnyTagValue("host") != "env:prod"

    def test_sorting(self):
        items = [AnyTagValue("host"), "env:prod", "color:blue"]
        items.sort()
        assert list(items) == ["color:blue", "env:prod", AnyTagValue("host")]

        items = ["env:prod", "color:blue", AnyTagValue("host"), "host"]
        items.sort()
        assert list(items) == ["color:blue", "env:prod", AnyTagValue("host"), "host"]

    def test_assertions(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["host:12345", "env:prod"])

            mm.assert_incr("test.key1", value=1, tags=[AnyTagValue("host"), "env:prod"])
            mm.assert_incr("test.key1", value=1, tags=["env:prod", AnyTagValue("host")])


class TestMetricsMock:
    """Verify the MetricsMock works as advertised"""

    def test_print_records(self):
        # NOTE(willkg): .print_records() prints to stdout and is mostly used
        # for debugging tests. So we're just going to run it and make sure it
        # doesn't throw errors.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1")

            mm.print_records()

    def test_clear_records(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            assert len(mm.get_records()) == 1

            mm.clear_records()

            assert len(mm.get_records()) == 0

    def test_filter_records_fun_name(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(stat="test.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="timing", stat="test.key1", value=1
            )
            assert len(key1_metrics) == 0

    def test_filter_records_key(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(fun_name="incr", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key2", value=1)
            assert len(key1_metrics) == 0

    def test_filter_records_value(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1")
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(fun_name="incr", stat="test.key1", value=5)
            assert len(key1_metrics) == 0

    def test_filter_records_tags(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1, tags=["env:stage"])
            mymetrics.incr("key2", value=3, tags=["env:prod"])

            key1_metrics = mm.filter_records(tags=["env:stage"])
            assert len(key1_metrics) == 1
            assert key1_metrics[0].key == "test.key1"

            key1_metrics = mm.filter_records(tags=["env:prod"])
            assert len(key1_metrics) == 1
            assert key1_metrics[0].key == "test.key2"

            key1_metrics = mm.filter_records(tags=["env:dev"])
            assert len(key1_metrics) == 0

    def test_has_record(self):
        # NOTE(willkg): .has_record() is implemented using .filter_records() so
        # we can test that aggressively and just make sure the .has_record()
        # wrapper works fine.
        #
        # If that ever changes, we should update this test.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1)

            assert mm.has_record(fun_name="incr", stat="test.key1", value=1)

            assert not mm.has_record(fun_name="incr", stat="test.key1", value=5)

    def test_configure_doesnt_affect_override(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1)

            assert mm.has_record(fun_name="incr", stat="test.key1", value=1)

            assert not mm.has_record(fun_name="incr", stat="test.key1", value=5)

    def test_incr_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.incr("key1", value=1)
            mymetrics.incr("keymultiple", value=1)
            mymetrics.incr("keymultiple", value=1)

            mm.assert_incr(stat="test.key1")

            mm.assert_incr_once(stat="test.key1")
            with pytest.raises(AssertionError):
                mm.assert_incr_once(stat="test.keymultiple")

            mm.assert_not_incr(stat="test.keynot")
            mm.assert_not_incr(stat="test.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_incr(stat="test.key1")

    def test_gauge_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.gauge("key1", value=5)
            mymetrics.gauge("keymultiple", value=5)
            mymetrics.gauge("keymultiple", value=5)

            mm.assert_gauge(stat="test.key1")

            mm.assert_gauge_once(stat="test.key1")
            with pytest.raises(AssertionError):
                mm.assert_gauge_once(stat="test.keymultiple")

            mm.assert_not_gauge(stat="test.keynot")
            mm.assert_not_gauge(stat="test.key1", value=10)
            with pytest.raises(AssertionError):
                mm.assert_not_gauge(stat="test.key1")

    def test_timing_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.timing("key1", value=1)
            mymetrics.timing("keymultiple", value=1)
            mymetrics.timing("keymultiple", value=1)

            mm.assert_timing(stat="test.key1")

            mm.assert_timing_once(stat="test.key1")
            with pytest.raises(AssertionError):
                mm.assert_timing_once(stat="test.keymultiple")

            mm.assert_not_timing(stat="test.keynot")
            mm.assert_not_timing(stat="test.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_timing(stat="test.key1")

    def test_histogram_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.histogram("key1", value=1)
            mymetrics.histogram("keymultiple", value=1)
            mymetrics.histogram("keymultiple", value=1)

            mm.assert_histogram(stat="test.key1")

            mm.assert_histogram_once(stat="test.key1")
            with pytest.raises(AssertionError):
                mm.assert_histogram_once(stat="test.keymultiple")

            mm.assert_not_histogram(stat="test.keynot")
            mm.assert_not_histogram(stat="test.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_histogram(stat="test.key1")

    def test_print_on_failure(self, capsys):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("test")
            mymetrics.histogram("keymultiple", value=1)
            mymetrics.histogram("keymultiple", value=1)

            with pytest.raises(AssertionError):
                mm.assert_histogram_once(stat="test.keymultiple")

            # On assertion error, the assert_* methods will print the metrics
            # records to stdout.
            captured = capsys.readouterr()
            expected = (
                "<MetricsRecord type=histogram key=test.keymultiple value=1 tags=[]>\n"
                "<MetricsRecord type=histogram key=test.keymultiple value=1 tags=[]>\n"
            )
            assert captured.out == expected
