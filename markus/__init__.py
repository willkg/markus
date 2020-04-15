# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus.main import configure, get_metrics  # noqa

INCR = "incr"
GAUGE = "gauge"
TIMING = "timing"
HISTOGRAM = "histogram"

__all__ = ["configure", "get_metrics", "INCR", "GAUGE", "TIMING", "HISTOGRAM"]

__author__ = "Will Kahn-Greene"
__email__ = "willkg@mozilla.com"

# yyyymmdd
__releasedate__ = "20200415"
# x.y.z or x.y.z.dev0 -- semver
__version__ = "2.2.0"
