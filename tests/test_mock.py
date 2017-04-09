# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import markus
from markus.testing import MetricsMock


class TestMetricsMock:
    """Verify the MetricsMock works as advertised"""
    def test_print_records(self):
        # NOTE(willkg): .print_records() prints to stdout and is mostly used
        # for debugging tests. So we're just going to run it and make sure it
        # doesn't throw errors.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1')

            mm.print_records()

    def test_filter_records_fun_name(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1', value=1, tags=['env:stage'])

            key1_metrics = mm.filter_records(
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='timing',
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 0

    def test_filter_records_key(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1', value=1, tags=['env:stage'])

            key1_metrics = mm.filter_records(
                fun_name='incr',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key2',
                value=1,
            )
            assert len(key1_metrics) == 0

    def test_filter_records_value(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1', value=1, tags=['env:stage'])

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
                value=1,
            )
            assert len(key1_metrics) == 1

            key1_metrics = mm.filter_records(
                fun_name='incr',
                stat='foobar.key1',
                value=5,
            )
            assert len(key1_metrics) == 0

    def test_filter_records_tags(self):
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1', value=1, tags=['env:stage'])
            mymetrics.incr('key2', value=3, tags=['env:prod'])

            key1_metrics = mm.filter_records(
                tags=['env:stage'],
            )
            assert len(key1_metrics) == 1
            assert key1_metrics[0][1] == 'foobar.key1'

            key1_metrics = mm.filter_records(
                tags=['env:prod'],
            )
            assert len(key1_metrics) == 1
            assert key1_metrics[0][1] == 'foobar.key2'

            key1_metrics = mm.filter_records(
                tags=['env:dev'],
            )
            assert len(key1_metrics) == 0

    def test_has_record(self):
        # NOTE(willkg): .has_record() is implemented using .filter_records() so
        # we can test that aggressively and just make sure the .has_record()
        # wrapper works fine.
        #
        # If that ever changes, we should update this test.
        with MetricsMock() as mm:
            mymetrics = markus.get_metrics('foobar')
            mymetrics.incr('key1', value=1)

            assert mm.has_record(
                fun_name='incr',
                stat='foobar.key1',
                value=1,
            )

            assert not mm.has_record(
                fun_name='incr',
                stat='foobar.key1',
                value=5,
            )
