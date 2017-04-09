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

    def _add_record(self, fun_name, stat, value, tags):
        self.records.append((fun_name, stat, value, tags))

    def incr(self, stat, value=1, tags=None):
        self._add_record(INCR, stat, value, tags)

    def gauge(self, stat, value, tags=None):
        self._add_record(GAUGE, stat, value, tags)

    def timing(self, stat, value, tags=None):
        self._add_record(TIMING, stat, value, tags)

    def histogram(self, stat, value, tags=None):
        self._add_record(HISTOGRAM, stat, value, tags)

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

    def filter_records(self, fun_name=None, stat=None, value=None, tags=None):
        """Filters collected metircs records for ones that match specified criteria"""
        def match_fun_name(record_fun_name):
            return fun_name is None or fun_name == record_fun_name

        def match_stat(record_stat):
            return stat is None or stat == record_stat

        def match_value(record_value):
            return value is None or value == record_value

        def match_tags(record_tags):
            return tags is None or list(sorted(tags)) == list(sorted(record_tags))

        return [
            record for record in self.get_records()
            if (match_fun_name(record[0]) and
                match_stat(record[1]) and
                match_value(record[2]) and
                match_tags(record[3]))
        ]

    def has_record(self, fun_name=None, stat=None, value=None, tags=None):
        """Returns True/False regarding whether collected metrics match specified criteria"""
        return bool(
            self.filter_records(
                fun_name=fun_name,
                stat=stat,
                value=value,
                tags=tags
            )
        )

    def print_records(self):
        """Prints all the collected metrics"""
        for record in self.get_records():
            print(record)
