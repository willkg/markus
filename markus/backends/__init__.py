# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class BackendBase(object):
    """Markus Backend superclass that defines API backends should follow."""

    def __init__(self, options):
        """Implement this. The options dict is the user-specified options."""
        self.options = options

    def emit(self, record):
        """Implement this to emit records."""
        raise NotImplementedError
