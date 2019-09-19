# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class BackendBase(object):
    """Markus Backend superclass that defines API backends should follow."""

    def __init__(self, options=None, filters=None):
        """Implement this.

        :arg dict options: user-specified options
        :arg list filters: filters to apply to this backend

        """
        self.options = options or {}
        self.filters = filters or []

    def _filter(self, record):
        for metrics_filter in self.filters:
            record = metrics_filter.filter(record)
            if record is None:
                return
        return record

    def emit_to_backend(self, record):
        """Emit record for backend handling.

        :arg MetricsRecord record: the record to be emitted

        """
        record = self._filter(record)
        if record is not None:
            self.emit(record)

    def emit(self, record):
        """Emit record to backend.

        Implement this in your backend.

        :arg MetricsRecord record: the record to be published

        """
        raise NotImplementedError
