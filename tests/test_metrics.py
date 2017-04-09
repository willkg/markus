import pytest

from markus import get_metrics
from markus.testing import MetricsMock


@pytest.fixture
def metricsmock():
    return MetricsMock()


@pytest.mark.parametrize('name, expected', [
    ('', ''),
    ('.', ''),
    ('abc(123)', 'abc.123'),
    ('...ab..c...', 'ab.c'),
])
def test_get_metrics_fix_name(name, expected):
    assert get_metrics(name).name == expected


class Foo(object):
    pass


@pytest.mark.parametrize('thing, extra, expected', [
    # Test base
    ('string', '', 'string'),
    (Foo, '', 'test_metrics.Foo'),
    (Foo(), '', 'test_metrics.Foo'),
    (__name__, '', 'test_metrics'),
    (None, '', ''),

    # Test extra
    ('foo', 'namespace1', 'foo.namespace1'),
])
def test_get_metrics(thing, extra, expected):
    assert get_metrics(thing, extra=extra).name == expected


def test_incr(metricsmock):
    metrics = get_metrics('thing')

    with metricsmock as mm:
        metrics.incr('foo', value=5)

    assert (
        mm.get_records() ==
        [
            ('incr', 'thing.foo', 5, None)
        ]
    )


def test_gauge(metricsmock):
    metrics = get_metrics('thing')

    with metricsmock as mm:
        metrics.gauge('foo', value=10)

    assert (
        mm.get_records() ==
        [
            ('gauge', 'thing.foo', 10, None)
        ]
    )


def test_timing(metricsmock):
    metrics = get_metrics('thing')

    with metricsmock as mm:
        metrics.timing('foo', value=1234)

    assert (
        mm.get_records() ==
        [
            ('timing', 'thing.foo', 1234, None)
        ]
    )


def test_histogram(metricsmock):
    metrics = get_metrics('thing')

    with metricsmock as mm:
        metrics.histogram('foo', value=4321)

    assert (
        mm.get_records() ==
        [
            ('histogram', 'thing.foo', 4321, None)
        ]
    )


def test_timer_contextmanager(metricsmock):
    metrics = get_metrics('thing')

    with metricsmock as mm:
        with metrics.timer('long_fun'):
            print('blah')

    assert mm.has_record(fun_name='timing', stat='thing.long_fun')


def test_timer_decorator(metricsmock):
    metrics = get_metrics('thing')

    @metrics.timer_decorator('long_fun')
    def something():
        print('blah')

    with metricsmock as mm:
        something()

    assert mm.has_record(fun_name='timing', stat='thing.long_fun')
