# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class BackendBase(object):
    """Markus Backend superclass that defines API backends should follow"""
    def __init__(self, options):
        self.options = options

    def incr(self, stat, **kwargs):
        raise NotImplementedError

    def gauge(self, stat, **kwargs):
        raise NotImplementedError

    def timing(self, stat, **kwargs):
        raise NotImplementedError

    def histogram(self, stat, **kwargs):
        raise NotImplementedError
