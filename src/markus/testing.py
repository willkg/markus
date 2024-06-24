# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from copy import copy
import functools
from types import TracebackType
from typing import List, Optional, Type, Union

from markus import INCR, GAUGE, TIMING, HISTOGRAM  # noqa
from markus.main import _override_metrics, MetricsRecord


__all__ = ["AnyTagValue", "MetricsMock"]


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


@functools.total_ordering
class AnyTagValue:
    """Matches a markus metrics tag with any value

    Example::

        import markus

        from markus.testing import AnyTagValue, MetricsMock


        with MetricsMock() as mm:
            metrics = get_metrics("test")

            metrics.incr("key1", value=1, tags=["host:12345"])

            mm.assert_incr(stat="test.key1", tags=[AnyTagValue("host")])

    """

    def __init__(self, key: str):
        self.key = key

    def __repr__(self):
        return f"<AnyTagValue {self.key}>"

    def get_other_key(self, other: str) -> str:
        # This is comparing against a tag string
        if ":" in other:
            other_key, _ = other.split(":")
        else:
            other_key = other
        return other_key

    def __eq__(self, other: Union[str, "AnyTagValue"]) -> bool:
        if isinstance(other, AnyTagValue):
            return self.key == other.key
        return self.key == self.get_other_key(other)

    def __lt__(self, other: Union[str, "AnyTagValue"]) -> bool:
        if isinstance(other, AnyTagValue):
            return self.key < other.key
        return self.key < self.get_other_key(other)


class MetricsMock:
    """Mock for recording metrics events and testing them.

    Mimics a metrics backend as a context manager. Keeps records of what got
    metricfied so that you can print them out, filter them, assert various
    things about them, etc.

    To use::

        from markus.testing import MetricsMock

        def test_something():
            with MetricsMock() as mm:
                # Do things that might record metrics here

                # Assert something about the metrics recorded
                mm.assert_incr_once(stat="some.random.key", value=1)

    When using the ``assert_*`` helper methods, if the assertion fails, it'll
    print the MetricsRecords that were emitted to stdout.

    """

    def __init__(self):
        self.records = []

    def emit_to_backend(self, record: MetricsRecord):
        self.emit(record)

    def emit(self, record: MetricsRecord):
        self.records.append(copy(record))

    def __enter__(self) -> "MetricsMock":
        self.records = []
        _override_metrics([self])
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> bool:
        _override_metrics(None)

    def get_records(self) -> List[MetricsRecord]:
        """Return list of MetricsRecord instances.

        This is the list of :py:class:`markus.main.MetricsRecord` instances
        that were emitted while this :py:class:`markus.testing.MetricsMock` was
        active.

        """
        return self.records

    def filter_records(
        self,
        fun_name: Optional[str] = None,
        stat: Optional[str] = None,
        value: Optional[Union[int, float]] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ) -> List[MetricsRecord]:
        """Filter collected metrics records for ones that match specified criteria.

        Filtering is done by ANDing the requirements together. For example::

            with MetricsMock() as mm:
                # Do something that emits metrics

                assert mm.filter_records("incr", stat="some.key", tags=["color:blue"])

        :py:meth:`markus.testing.MetricsMock.filter_records` will return
        :py:class:`markus.main.MetricsRecord` instances that are ``"incr"`` AND
        the stat is ``"some.key"`` AND the tags list is ``["color:blue"]``.

        :arg fun_name: "incr", "gauge", "timing", "histogram", or ``None``
        :arg stat: the stat emitted
        :arg value: the value
        :arg tags: the list of tag strings or ``[]`` or ``None``

        :returns: list of :py:class:`markus.main.MetricsRecord` instances

        """

        def match_fun_name(record_fun_name: Optional[str]) -> bool:
            return fun_name is None or fun_name == record_fun_name

        def match_stat(record_stat: Optional[str]) -> bool:
            return stat is None or stat == record_stat

        def match_value(record_value: Optional[Union[int, float]]) -> bool:
            return value is None or value == record_value

        def match_tags(record_tags: Optional[List[Union[str, AnyTagValue]]]) -> bool:
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

    def has_record(
        self,
        fun_name: Optional[str] = None,
        stat: Optional[str] = None,
        value: Optional[Union[int, float]] = None,
        tags=None,
    ) -> bool:
        """Return True/False regarding whether collected metrics match criteria.

        :arg fun_name: "incr", "gauge", "timing", "histogram", or ``None``
        :arg stat: the stat emitted
        :arg value: the value
        :arg tags: the list of tag strings or ``[]`` or ``None``

        :returns: bool

        """
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
    def assert_incr(
        self,
        stat: Optional[str],
        value: Optional[int] = 1,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts an incr was emitted at least once."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_incr_once(
        self,
        stat: Optional[str],
        value: Optional[int] = 1,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts an incr was emitted exactly once."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_incr(
        self,
        stat: Optional[str],
        value: Optional[int] = 1,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts an incr was not emitted."""
        assert len(self.filter_records(INCR, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_gauge(
        self,
        stat: Optional[str],
        value: Optional[int] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a gauge was emitted at least once."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_gauge_once(
        self,
        stat: Optional[str],
        value: Optional[int] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a gauge was emitted exactly once."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_gauge(
        self,
        stat: Optional[str],
        value: Optional[int] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a gauge was not emitted."""
        assert len(self.filter_records(GAUGE, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_timing(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a timing was emitted at least once."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) >= 1

    @print_on_failure
    def assert_timing_once(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a timing was emitted exactly once."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) == 1

    @print_on_failure
    def assert_not_timing(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a timing was not emitted."""
        assert len(self.filter_records(TIMING, stat=stat, value=value, tags=tags)) == 0

    @print_on_failure
    def assert_histogram(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a histogram was emitted at least once."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) >= 1
        )

    @print_on_failure
    def assert_histogram_once(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a histogram was emitted exactly once."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) == 1
        )

    @print_on_failure
    def assert_not_histogram(
        self,
        stat: Optional[str],
        value: Optional[float] = None,
        tags: Optional[List[Union[str, AnyTagValue]]] = None,
    ):
        """Asserts a histogram was not emitted."""
        assert (
            len(self.filter_records(HISTOGRAM, stat=stat, value=value, tags=tags)) == 0
        )
