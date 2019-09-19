# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from markus.main import MetricsFilter


class AddTagFilter(MetricsFilter):
    """Metrics filter that adds tags.

    Contrived example that adds the host for all metrics generated in this
    module::

        import markus
        from markus.main import AddTagFilter

        from someplace import get_host

        metrics = markus.get_metrics(
            __name__,
            filters=[AddTag("host:" + get_host())]
        )

    """

    def __init__(self, tag):
        self.tag = tag

    def filter(self, record):
        record.tags.append(self.tag)
        return record
