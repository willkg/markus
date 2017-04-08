# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus import INCR, GAUGE, TIMING, HISTOGRAM

from markus.main import _change_metrics, _get_metrics_backends


class MetricsMock:
    """Mock for recording metrics events and testing them

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
                mm.print_metrics()

                # Assert something about the metrics recorded
                assert mm.has_record(INCR, 'some.random.key', {'value': 1})

    """
    def __init__(self):
        self.records = []
        self._old_backends = None

    def _add_record(self, fun_name, stat, kwargs):
        self.records.append((fun_name, stat, kwargs))

    def incr(self, stat, **kwargs):
        self._add_record(INCR, stat, kwargs)

    def gauge(self, stat, **kwargs):
        self._add_record(GAUGE, stat, kwargs)

    def timing(self, stat, **kwargs):
        self._add_record(TIMING, stat, kwargs)

    def histogram(self, stat, **kwargs):
        self._add_record(HISTOGRAM, stat, kwargs)

    def __enter__(self):
        self.records = []
        self._old_backends = _get_metrics_backends()
        _change_metrics([self])
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _change_metrics(self._old_backends)
        self._old_backends = None

    def get_records(self):
        """Returns set of collected metrics records"""
        return self.records

    def filter_records(self, fun_name=None, stat=None, kwargs_contains=None):
        """Filters collected metircs records for ones that match specified criteria"""
        def match_fun_name(record_fun_name):
            return fun_name is None or fun_name == record_fun_name

        def match_stat(record_stat):
            return stat is None or stat == record_stat

        def match_kwargs(record_kwargs):
            NO_VALUE = object()
            if kwargs_contains is None:
                return True
            for stat, val in record_kwargs.items():
                if kwargs_contains.get(stat, NO_VALUE) != val:
                    return False
            return True

        return [
            record for record in self.get_records()
            if (match_fun_name(record[0]) and
                match_stat(record[1]) and
                match_kwargs(record[2]))
        ]

    def has_record(self, fun_name=None, stat=None, kwargs_contains=None):
        """Returns True/False regarding whether collected metrics match specified criteria"""
        return bool(
            self.filter_records(
                fun_name=fun_name,
                stat=stat,
                kwargs_contains=kwargs_contains
            )
        )

    def print_records(self):
        """Prints all the collected metrics"""
        for record in self.get_records():
            print(record)
