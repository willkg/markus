import logging
import pytest

from markus import get_metrics
from markus.filters import (
    AddTagFilter,
    MetricsInvalidSchema,
    MetricsUnknownKey,
    MetricsWrongType,
    RegisteredMetricsFilter,
    _validate_registered_metrics,
)
from markus.main import MetricsRecord


logging.basicConfig()


def test_tag_filter(metricsmock):
    metrics = get_metrics("thing", filters=[AddTagFilter("foo:bar")])

    with metricsmock as mm:
        metrics.incr("foo", value=5)

    assert mm.get_records() == [
        MetricsRecord("incr", "thing.foo", 5, ["foo:bar"]),
    ]


@pytest.mark.parametrize(
    "schema",
    [
        pytest.param({}, id="empty"),
        pytest.param({"testkey": {"type": "incr", "description": "abcde"}}, id="basic"),
        pytest.param(
            {
                "testkey_incr": {"type": "incr", "description": "abcde"},
                "testkey_gauge": {"type": "gauge", "description": "abcde"},
                "testkey_timing": {"type": "timing", "description": "abcde"},
                "testkey_histogram": {"type": "histogram", "description": "abcde"},
            },
            id="cover_stats",
        ),
        pytest.param(
            {
                "testkey": {
                    "type": "incr",
                    "description": "abcde",
                    "labels": [],
                    "bugs": [],
                }
            },
            id="addtl_info",
        ),
    ],
)
def test_validate_registered_metrics(schema):
    _validate_registered_metrics(schema)


@pytest.mark.parametrize(
    "schema, error_msg",
    [
        pytest.param([], "registered_metrics is not a dict", id="not_dict"),
        pytest.param({1: {}}, "key 1 is not a str", id="key_not_str"),
        pytest.param(
            {"key": []}, "key 'key' has a non-dict value", id="non_dict_value"
        ),
        pytest.param(
            {"key": {"type": "incr"}},
            "key 'key' has value missing type or description",
            id="missing_description",
        ),
        pytest.param(
            {"key": {"description": "foo"}},
            "key 'key' has value missing type or description",
            id="missing_type",
        ),
        pytest.param(
            {"key": {"type": "foo", "description": "foo"}},
            "key 'key' type is foo; not one of incr, gauge, timing, histogram",
            id="invalid_type",
        ),
        pytest.param(
            {"key": {"type": "incr", "description": 5}},
            "key 'key' description is not a str",
            id="bad_description_type",
        ),
    ],
)
def test_validate_registered_metrics_invalid(schema, error_msg):
    with pytest.raises(MetricsInvalidSchema) as excinfo:
        _validate_registered_metrics(schema)

    assert str(excinfo.value) == error_msg


ALLOWED_METRICS = {
    "thing.key_incr": {
        "type": "incr",
        "description": "--",
    },
    "thing.key_gauge": {
        "type": "gauge",
        "description": "--",
    },
    "thing.key_timing": {
        "type": "timing",
        "description": "--",
    },
    "thing.key_histogram": {
        "type": "histogram",
        "description": "--",
    },
}


def test_registered_metrics_filter(caplog, metricsmock):
    caplog.set_level(logging.INFO)

    metrics = get_metrics(
        "thing", filters=[RegisteredMetricsFilter(ALLOWED_METRICS, raise_error=False)]
    )

    with metricsmock as mm:
        # Emit allowed metrics
        metrics.incr("key_incr", value=1)
        metrics.gauge("key_gauge", value=10)
        metrics.timing("key_timing", value=1.0)
        metrics.histogram("key_histogram", value=10.0)

        assert mm.get_records() == [
            MetricsRecord("incr", "thing.key_incr", 1, []),
            MetricsRecord("gauge", "thing.key_gauge", 10, []),
            MetricsRecord("timing", "thing.key_timing", 1.0, []),
            MetricsRecord("histogram", "thing.key_histogram", 10.0, []),
        ]

    assert caplog.records == []


def test_registered_metrics_filter_missing(caplog, metricsmock):
    caplog.set_level(logging.INFO)

    metrics = get_metrics(
        "thing", filters=[RegisteredMetricsFilter(ALLOWED_METRICS, raise_error=False)]
    )

    with metricsmock as mm:
        # Emit unknown metric
        metrics.incr("unknown_key", value=1)

        assert mm.get_records() == [
            MetricsRecord("incr", "thing.unknown_key", 1, []),
        ]

    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "metrics key 'thing.unknown_key' is unknown."


def test_registered_metrics_filter_missing_error(metricsmock):
    with pytest.raises(MetricsUnknownKey) as excinfo:
        metrics = get_metrics(
            "thing",
            filters=[RegisteredMetricsFilter(ALLOWED_METRICS, raise_error=True)],
        )
        with metricsmock:
            # Emit unknown metric
            metrics.incr("unknown_key", value=1)

    assert str(excinfo.value) == "metrics key 'thing.unknown_key' is unknown"


def test_registered_metrics_filter_bad_type(metricsmock):
    with pytest.raises(MetricsWrongType) as excinfo:
        metrics = get_metrics(
            "thing",
            filters=[RegisteredMetricsFilter(ALLOWED_METRICS, raise_error=True)],
        )
        with metricsmock:
            # Emit unknown metric
            metrics.incr("key_gauge", value=1)

    assert (
        str(excinfo.value)
        == "metrics key 'thing.key_gauge' has wrong type; incr vs. gauge"
    )
