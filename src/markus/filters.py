# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
from typing import Dict

from markus.main import MetricsFilter, MetricsRecord


LOGGER = logging.getLogger(__name__)


class MetricsException(Exception):
    pass


class MetricsInvalidSchema(MetricsException):
    pass


class MetricsUnknownKey(MetricsException):
    pass


class MetricsWrongType(MetricsException):
    pass


RegisteredMetricsType = Dict[str, Dict[str, str]]


def _validate_registered_metrics(registered_metrics: RegisteredMetricsType):
    if not isinstance(registered_metrics, dict):
        raise MetricsInvalidSchema("registered_metrics is not a dict")

    for key, val in registered_metrics.items():
        if not isinstance(key, str):
            raise MetricsInvalidSchema(f"key {key!r} is not a str")

        if not isinstance(val, dict):
            raise MetricsInvalidSchema(f"key {key!r} has a non-dict value")

        if "type" not in val.keys() or "description" not in val.keys():
            raise MetricsInvalidSchema(
                f"key {key!r} has value missing type or description"
            )

        if val["type"] not in ["incr", "gauge", "timing", "histogram"]:
            raise MetricsInvalidSchema(
                f"key {key!r} type is {val['type']}; "
                + "not one of incr, gauge, timing, histogram"
            )

        if not isinstance(val["description"], str):
            raise MetricsInvalidSchema(f"key {key!r} description is not a str")


class RegisteredMetricsFilter(MetricsFilter):
    """Contains a list of registered metrics and validator.

    This is a Markus Metrics filter. It'll complain if metrics are generated
    that it doesn't know about.

    Registered metrics should be a dict structured like this::

        {
            KEY -> {
                "type": str,         # one of "incr" | "gauge" | "timing" | "histogram"
                "description": str,  # can use markdown
            },
            ...
        }

    For example::

        {
            "eliot.symbolicate_api": {
                "type": "timing",
                "description": "Timer for how long a symbolication API request takes.",
            },
            "eliot.symbolicate.proxied": {
                "type": "incr",
                description": "Counter for symbolication requests.",
            },
            ...
        }

    You can include additional information to suit your needs::

        {
            "eliot.symbolicate_api": {
                "type": "timing",
                "description": "Timer for how long a symbolication API request takes.",
                "data_sensitivity": "technical",
                "bugs": [
                    "https://example.com/bugid=12345",
                ],
            },
            ...
        }

    You can define your metrics in JSON or YAML, read them in, and pass them to
    ``RegisteredMetricsFilter`` for easier management of metrics.

    """

    def __init__(
        self, registered_metrics: RegisteredMetricsType, raise_error: bool = False
    ):
        _validate_registered_metrics(registered_metrics)
        self.registered_metrics = registered_metrics
        self.raise_error = raise_error

    def __repr__(self):
        return f"<RegisteredMetricsFilter {len(self.registered_metrics)} {self.raise_error}>"

    def filter(self, record: MetricsRecord) -> MetricsRecord:
        metric = self.registered_metrics.get(record.key)
        if metric is None:
            if self.raise_error:
                raise MetricsUnknownKey(f"metrics key {record.key!r} is unknown")
            LOGGER.warning("metrics key %r is unknown.", record.key)

        elif record.stat_type != metric["type"]:
            if self.raise_error:
                raise MetricsWrongType(
                    f"metrics key {record.key!r} has wrong type; {record.stat_type} vs. "
                    + f"{metric['type']}"
                )

            LOGGER.warning(
                "metrics key %r has wrong type; got %s expecting %s",
                record.key,
                record.stat_type,
                metric["type"],
            )

        return record


class AddTagFilter(MetricsFilter):
    """Metrics filter that adds tags.

    Contrived example that adds the host for all metrics generated in this
    module::

        import socket

        import markus
        from markus.filters import AddTagFilter

        metrics = markus.get_metrics(
            __name__,
            filters=[AddTagFilter(f"host:{socket.gethostname()}")]
        )

    """

    def __init__(self, tag: str):
        self.tag = tag

    def __repr__(self):
        return f"<AddTagFilter {self.tag}>"

    def filter(self, record: MetricsRecord) -> MetricsRecord:
        record.tags.append(self.tag)
        return record
