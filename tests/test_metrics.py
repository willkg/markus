import pytest

from markus import get_metrics
from markus.filters import AddTagFilter
from markus.main import MetricsRecord
from markus.testing import MetricsMock


@pytest.fixture
def metricsmock():
    return MetricsMock()


@pytest.mark.parametrize(
    "prefix, expected",
    [("", ""), (".", ""), ("abc(123)", "abc.123"), ("...ab..c...", "ab.c")],
)
def test_get_metrics_fix_name(prefix, expected):
    assert get_metrics(prefix).prefix == expected


class Foo:
    pass


@pytest.mark.parametrize(
    "thing, extra, expected",
    [
        # Test base
        ("string", "", "string"),
        (Foo, "", "test_metrics.Foo"),
        (Foo(), "", "test_metrics.Foo"),
        (__name__, "", "test_metrics"),
        (None, "", ""),
        # Test extra
        ("foo", "namespace1", "foo.namespace1"),
    ],
)
def test_get_metrics_prefix(thing, extra, expected):
    assert get_metrics(thing, extra=extra).prefix == expected


def test_metricsinterface_extend_prefix():
    metrics = get_metrics("a")
    sub_metrics = metrics.extend_prefix("b")
    assert sub_metrics.prefix == "a.b"
    assert sub_metrics.filters == []

    sub_metrics = metrics.extend_prefix(".b.")
    assert sub_metrics.prefix == "a.b"
    assert sub_metrics.filters == []

    tag_filter_host_foo = AddTagFilter("host:foo")

    metrics.filters.append(tag_filter_host_foo)
    sub_metrics = metrics.extend_prefix("b")
    assert sub_metrics.prefix == "a.b"
    assert sub_metrics.filters == [tag_filter_host_foo]

    tag_filter_env_prod = AddTagFilter("env:prod")
    # Add a second tag filter and make sure the two lists are independent
    metrics.filters.append(tag_filter_env_prod)
    assert metrics.filters == [tag_filter_host_foo, tag_filter_env_prod]
    assert sub_metrics.filters == [tag_filter_host_foo]


def test_dunders():
    record = MetricsRecord("incr", "foo", 10, [])
    record2 = record.__copy__()
    assert record is not record2
    assert record == record2


def test_incr(metricsmock):
    metrics = get_metrics("thing")

    with metricsmock as mm:
        metrics.incr("foo", value=5)

    assert mm.get_records() == [MetricsRecord("incr", "thing.foo", 5, [])]


def test_gauge(metricsmock):
    metrics = get_metrics("thing")

    with metricsmock as mm:
        metrics.gauge("foo", value=10)

    assert mm.get_records() == [MetricsRecord("gauge", "thing.foo", 10, [])]


def test_timing(metricsmock):
    metrics = get_metrics("thing")

    with metricsmock as mm:
        metrics.timing("foo", value=1234)

    assert mm.get_records() == [MetricsRecord("timing", "thing.foo", 1234, [])]


def test_histogram(metricsmock):
    metrics = get_metrics("thing")

    with metricsmock as mm:
        metrics.histogram("foo", value=4321)

    assert mm.get_records() == [MetricsRecord("histogram", "thing.foo", 4321, [])]


def test_timer_contextmanager(metricsmock):
    metrics = get_metrics("thing")

    with metricsmock as mm:
        with metrics.timer("long_fun"):
            print("blah")

    assert mm.has_record(fun_name="timing", stat="thing.long_fun")


def test_timer_decorator(metricsmock):
    metrics = get_metrics("thing")

    @metrics.timer_decorator("long_fun")
    def something():
        print("blah")

    with metricsmock as mm:
        something()

    assert mm.has_record(fun_name="timing", stat="thing.long_fun")
