# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class BackendBase(object):
    """Markus Backend superclass that defines API backends should follow"""
    def __init__(self, options):
        """Implement this. The options dict is the user-specified options."""
        self.options = options

    def incr(self, stat, value=1, tags=None):
        """Implement this. This is a counter-type metric."""
        raise NotImplementedError

    def gauge(self, stat, value, tags=None):
        """Implement this. This is a gauge-type metric."""
        raise NotImplementedError

    def timing(self, stat, value, tags=None):
        """Implement this. This is a timing-type metric."""
        raise NotImplementedError

    def histogram(self, stat, value, tags=None):
        """Implement this. This is a histogram-type metric."""
        raise NotImplementedError
