# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from markus.backends import datadog


class MockDogStatsd(object):
    def __init__(self, *args, **kwargs):
        self.initargs = args
        self.initkwargs = kwargs
        self.calls = []

    def increment(self, *args, **kwargs):
        self.calls.append(
            ('increment', args, kwargs),
        )

    def gauge(self, *args, **kwargs):
        self.calls.append(
            ('gauge', args, kwargs)
        )

    def timing(self, *args, **kwargs):
        self.calls.append(
            ('timing', args, kwargs)
        )

    def histogram(self, *args, **kwargs):
        self.calls.append(
            ('histogram', args, kwargs)
        )


@pytest.yield_fixture
def mockdogstatsd():
    """Mocks DogStatsd class to capture method call data"""
    _old_datadog = datadog.DogStatsd
    mock = MockDogStatsd
    datadog.DogStatsd = mock
    yield
    datadog.DogStatsd = _old_datadog


def test_default_options(mockdogstatsd):
    ddm = datadog.DatadogMetrics({})

    assert ddm.host == 'localhost'
    assert ddm.port == 8125
    assert ddm.namespace == ''

    # NOTE(willkg): ddm.client is the mock instance
    assert ddm.client.initargs == ()
    assert ddm.client.initkwargs == {'host': 'localhost', 'port': 8125, 'namespace': ''}


def test_options(mockdogstatsd):
    ddm = datadog.DatadogMetrics({
        'statsd_host': 'example.com',
        'statsd_port': 5000,
        'statsd_namespace': 'joe',
    })

    assert ddm.host == 'example.com'
    assert ddm.port == 5000
    assert ddm.namespace == 'joe'

    # NOTE(willkg): ddm.client is the mock instance
    assert ddm.client.initargs == ()
    assert ddm.client.initkwargs == {'host': 'example.com', 'port': 5000, 'namespace': 'joe'}


def test_incr(mockdogstatsd):
    ddm = datadog.DatadogMetrics({})

    ddm.incr('foo', value=10, tags=['key1:val'])

    assert (
        ddm.client.calls ==
        [('increment', (), {'metric': 'foo', 'value': 10, 'tags': ['key1:val']})]
    )


def test_gauge(mockdogstatsd):
    ddm = datadog.DatadogMetrics({})

    ddm.gauge('foo', value=100, tags=['key1:val'])

    assert (
        ddm.client.calls ==
        [('gauge', (), {'metric': 'foo', 'value': 100, 'tags': ['key1:val']})]
    )


def test_timing(mockdogstatsd):
    ddm = datadog.DatadogMetrics({})

    ddm.timing('foo', value=1234, tags=['key1:val'])

    assert (
        ddm.client.calls ==
        [('timing', (), {'metric': 'foo', 'value': 1234, 'tags': ['key1:val']})]
    )


def test_histogram(mockdogstatsd):
    ddm = datadog.DatadogMetrics({})

    ddm.histogram('foo', value=4321, tags=['key1:val'])

    assert (
        ddm.client.calls ==
        [('histogram', (), {'metric': 'foo', 'value': 4321, 'tags': ['key1:val']})]
    )
