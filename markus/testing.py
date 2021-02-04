# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from copy import copy

import functools

from markus import INCR, GAUGE, TIMING, HISTOGRAM  # noqa
from markus.main import _override_metrics


def print_on_failure(fun):
    """Decorator to print metrics records on assertion failure."""

    @functools.wraps(fun)
    def _print_on_failure(metricsmock, *args, **kwargs):
        try:
            return fun(metricsmock, *args, **kwargs)
        except Exception:
            metricsmock.print_records()
            raise

    return _print_on_failure


class MetricsMock:
    """Mock for recording metrics events and testing them.

    Mimics a metrics backend as a context manager. Keeps records of what got
    metricfied so that you can print them out, filter them, assert various
    things about them, etc.

    To use::

        from markus.testing import MetricsMock
        from markus import INCR, GAUGE, TIMING, HISTOGRAM


        def test_something():
            with MetricsMock() as mm:
                # do things that might record metrics

                # Print the metrics recorded (helps with debugging)
                mm.print_records()

                # Assert something about the metrics recorded
                assert mm.has_record(INCR, stat='some.random.key', value=1)

    """

    def __init__(self):
        self.records = []

    def emit_to_backend(self, record):
        self.emit(record)

    def emit(self, record):
        self.records.append(copy(record))

    def __enter__(self):
        self.records = []
        _override_metrics([self])
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _override_metrics(None)

    def get_records(self):
        """Return set of collected metrics records."""
        return self.records

    def filter_records(self, fun_name=None, stat=None, value=None, tags=None):
        """Filter collected metircs records for ones that match specified criteria."""

        def match_fun_name(record_fun_name):
            return fun_name is None or fun_name == record_fun_name

        def match_stat(record_stat):
            return stat is None or stat == record_stat

        def match_value(record_value):
            return value is None or value == record_value

        def match_tags(record_tags):
            return tags is None or list(sorted(tags)) == list(sorted(record_tags))

        return [
            record
            for record in self.get_records()
            if (
                match_fun_name(record.stat_type)
                and match_stat(record.key)
                and match_value(record.value)
                and match_tags(record.tags)
            )
        ]

    def has_record(self, fun_name=None, stat=None, value=None, tags=None):
        """Return True/False regarding whether collected metrics match criteria."""
        return bool(
            self.filter_records(fun_name=fun_name, stat=stat, value=value, tags=tags)
        )

    def print_records(self):
        """Print all the collected metrics."""
        for record in self.get_records():
            print(f"{record!r}")

    def clear_records(self):
        """Clear the records list."""
        self.records = []

    @print_on_failure
    def assert_incr(self, stat, value=1, tags=None):
        """Asserts an incr was emitted at least once."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_incr_once(self, stat, value=1, tags=None):
        """Asserts an incr was emitted exactly once."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_incr(self, stat, value=1, tags=None):
        """Asserts an incr was not emitted."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_gauge(self, stat, value=None, tags=None):
        """Asserts a gauge was emitted at least once."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_gauge_once(self, stat, value=None, tags=None):
        """Asserts a gauge was emitted exactly once."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_gauge(self, stat, value=None, tags=None):
        """Asserts a gauge was not emitted."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_timing(self, stat, value=None, tags=None):
        """Asserts a timing was emitted at least once."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_timing_once(self, stat, value=None, tags=None):
        """Asserts a timing was emitted exactly once."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_timing(self, stat, value=None, tags=None):
        """Asserts a timing was not emitted."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_histogram(self, stat, value=None, tags=None):
        """Asserts a histogram was emitted at least once."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) >= 1
        )

    @print_on_failure
    def assert_histogram_once(self, stat, value=None, tags=None):
        """Asserts a histogram was emitted exactly once."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) == 1
        )

    @print_on_failure
    def assert_not_histogram(self, stat, value=None, tags=None):
        """Asserts a histogram was not emitted."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) == 0
        )
