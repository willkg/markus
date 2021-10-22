# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

try:
    # Enable pytest assert rewriting for better assert debugging
    import pytest

    pytest.register_assert_rewrite("markus.testing")
except ImportError:
    pass

from markus.main import configure, get_metrics  # noqa

INCR = "incr"
GAUGE = "gauge"
TIMING = "timing"
HISTOGRAM = "histogram"

__all__ = ["configure", "get_metrics", "INCR", "GAUGE", "TIMING", "HISTOGRAM"]

__author__ = "Will Kahn-Greene"
__email__ = "willkg@mozilla.com"

# yyyymmdd
__releasedate__ = "20210205"
# x.y.z or x.y.z.dev0 -- semver
__version__ = "3.0.0"
