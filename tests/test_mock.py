# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import markus
from markus.testing import MetricsMock

import pytest


class TestMetricsMock:
    """Verify the MetricsMock works as advertised"""

    def test_print_records(self):
        # NOTE(willkg): .print_records() prints to stdout and is mostly used
        # for debugging tests. So we're just going to run it and make sure it
        # doesn't throw errors.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1")

            mm.print_records()

    def test_clear_records(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            assert len(mm.get_records()) == 1

            mm.clear_records()

            assert len(mm.get_records()) == 0

    def test_filter_records_fun_name(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(stat="foobar.key1", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key1", value=1
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="timing", stat="foobar.key1", value=1
            )
            assert len(key1_metrics) == 0

    def test_filter_records_key(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(fun_name="incr", value=1)
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key1", value=1
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key1", value=1
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key2", value=1
            )
            assert len(key1_metrics) == 0

    def test_filter_records_value(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1, tags=["env:stage"])

            key1_metrics = mm.filter_records(fun_name="incr", stat="foobar.key1")
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key1", value=1
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name="incr", stat="foobar.key1", value=5
            )
            assert len(key1_metrics) == 0

    def test_filter_records_tags(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1, tags=["env:stage"])
            mymetrics.incr("key2", value=3, tags=["env:prod"])

            key1_metrics = mm.filter_records(tags=["env:stage"])
            assert len(key1_metrics) == 1
            assert key1_metrics[0][1] == "foobar.key1"

            key1_metrics = mm.filter_records(tags=["env:prod"])
            assert len(key1_metrics) == 1
            assert key1_metrics[0][1] == "foobar.key2"

            key1_metrics = mm.filter_records(tags=["env:dev"])
            assert len(key1_metrics) == 0

    def test_has_record(self):
        # NOTE(willkg): .has_record() is implemented using .filter_records() so
        # we can test that aggressively and just make sure the .has_record()
        # wrapper works fine.
        #
        # If that ever changes, we should update this test.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1)

            assert mm.has_record(fun_name="incr", stat="foobar.key1", value=1)

            assert not mm.has_record(fun_name="incr", stat="foobar.key1", value=5)

    def test_configure_doesnt_affect_override(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1)

            assert mm.has_record(fun_name="incr", stat="foobar.key1", value=1)

            assert not mm.has_record(fun_name="incr", stat="foobar.key1", value=5)

    def test_incr_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("foobar")
            mymetrics.incr("key1", value=1)
            mymetrics.incr("keymultiple", value=1)
            mymetrics.incr("keymultiple", value=1)

            mm.assert_incr(stat="foobar.key1")

            mm.assert_incr_once(stat="foobar.key1")
            with pytest.raises(AssertionError):
                mm.assert_incr_once(stat="foobar.keymultiple")

            mm.assert_not_incr(stat="foobar.keynot")
            mm.assert_not_incr(stat="foobar.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_incr(stat="foobar.key1")

    def test_gauge_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("foobar")
            mymetrics.gauge("key1", value=5)
            mymetrics.gauge("keymultiple", value=5)
            mymetrics.gauge("keymultiple", value=5)

            mm.assert_gauge(stat="foobar.key1")

            mm.assert_gauge_once(stat="foobar.key1")
            with pytest.raises(AssertionError):
                mm.assert_gauge_once(stat="foobar.keymultiple")

            mm.assert_not_gauge(stat="foobar.keynot")
            mm.assert_not_gauge(stat="foobar.key1", value=10)
            with pytest.raises(AssertionError):
                mm.assert_not_gauge(stat="foobar.key1")

    def test_timing_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("foobar")
            mymetrics.timing("key1", value=1)
            mymetrics.timing("keymultiple", value=1)
            mymetrics.timing("keymultiple", value=1)

            mm.assert_timing(stat="foobar.key1")

            mm.assert_timing_once(stat="foobar.key1")
            with pytest.raises(AssertionError):
                mm.assert_timing_once(stat="foobar.keymultiple")

            mm.assert_not_timing(stat="foobar.keynot")
            mm.assert_not_timing(stat="foobar.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_timing(stat="foobar.key1")

    def test_histogram_helpers(self):
        with MetricsMock() as mm:
            markus.configure([{"class": "markus.backends.logging.LoggingMetrics"}])
            mymetrics = markus.get_metrics("foobar")
            mymetrics.histogram("key1", value=1)
            mymetrics.histogram("keymultiple", value=1)
            mymetrics.histogram("keymultiple", value=1)

            mm.assert_histogram(stat="foobar.key1")

            mm.assert_histogram_once(stat="foobar.key1")
            with pytest.raises(AssertionError):
                mm.assert_histogram_once(stat="foobar.keymultiple")

            mm.assert_not_histogram(stat="foobar.keynot")
            mm.assert_not_histogram(stat="foobar.key1", value=5)
            with pytest.raises(AssertionError):
                mm.assert_not_histogram(stat="foobar.key1")
