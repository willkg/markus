# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus.testing import MetricsMock

import pytest


pytest.register_assert_rewrite("markus.testing")


@pytest.fixture
def metricsmock() -> MetricsMock:
    with MetricsMock() as mm:
        yield mm
