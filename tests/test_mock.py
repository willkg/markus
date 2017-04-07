# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import markus
from markus.testing import MetricsMock


class TestMetricsMock:
    """Verify the MetricsMock works as advertised"""
    def test_print_metrics(self):
        # NOTE(willkg): .print_metrics() prints to stdout and is mostly used
        # for debugging tests. So we're just going to run it and make sure it
        # doesn't throw errors.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1')

            mm.print_metrics()

    def test_filter_metrics(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1')

            # Test fun_name match
            key1_metrics = mm.filter_metrics(
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='timing',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 0

            # Test key match
            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key2',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 0

            # Test kwargs_contains
            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_metrics(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 5}
            )
            assert len(key1_metrics) == 0

    def test_has_metric(self):
        # NOTE(willkg): .has_metric() is implemented using .filter_metrics() so
        # we can test that aggressively and just make sure the .has_metric()
        # wrapper works fine.
        #
        # If that ever changes, we should update this test.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1')

            assert mm.has_metric(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 1}
            )

            assert not mm.has_metric(
                fun_name='incr',
                stat='foobar.key1',
                kwargs_contains={'value': 5}
            )
