# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import contextlib
from functools import wraps
import logging
import re
import sys
import time


NOT_ALPHANUM_RE = re.compile(r"[^a-z0-9_\.]", re.I)
CONSECUTIVE_PERIODS_RE = re.compile(r"\.+")


logger = logging.getLogger(__name__)


_override_backends = None
_metrics_backends = []


def _override_metrics(backends):
    """Override backends for testing."""
    global _override_backends
    _override_backends = backends


def _change_metrics(backends):
    """Set a new backend."""
    global _metrics_backends
    _metrics_backends = backends


def _get_metrics_backends():
    return _override_backends or _metrics_backends


def split_clspath(clspath):
    """Split of clspath into module and class name.

    NOTE(willkg): This is really simple. Maybe we should use something more
    sophisticated?

    """
    return clspath.rsplit(".", 1)


def configure(backends, raise_errors=False):
    """Instantiate and configures backends.

    :arg list-of-dicts backends: the backend configuration as a list of dicts where
        each dict specifies a separate backend.

        Each backend dict consists of three things:

        1. ``class`` with a value that is either a Python class or a dotted
           Python path to one

        2. (optional) ``options`` dict with options for the backend in question
           to configure it

        3. (optional) ``filters`` list of filters to apply to metrics emitted
           by this backend

        See the documentation for the backends you're using to know what is
        configurable in the options dict.

    :arg raise_errors bool: whether or not to raise an exception if something
        happens in configuration; if it doesn't raise an exception, it'll log
        the exception

    For example, this sets up a default
    :py:class:`markus.backends.logging.LoggingMetrics` backend::

        import markus

        markus.configure([
            {
                'class': 'markus.backends.logging.LoggingMetrics',
            }
        ])

    This sets up a
    :py:class:`markus.backends.logging.LoggingMetrics` backend with
    options::

        import markus

        markus.configure([
            {
                'class': 'markus.backends.logging.LoggingMetrics',
                'options': {
                    'logger_name': 'metrics'
                }
            }
        ])

    This sets up a :py:class:`markus.backends.logging.LoggingMetrics`
    backend that adds a tag to every metric::

        import markus
        from markus.filters import AddTagFilter

        markus.configure([
            {
                'class': 'markus.backends.logging.LoggingMetrics',
                'filters': [AddTagFilter("color:blue")],
            }
        ])

    You can set up zero or more backends.

    .. Note::

       During application startup, Markus should get configured before the app
       starts generating metrics. Any metrics generated before Markus is
       configured will get dropped.

       However, anything can call :py:func:`markus.get_metrics` and get a
       :py:class:`markus.main.MetricsInterface` before Markus has been
       configured including at module load time.

    """
    good_backends = []

    for backend in backends:
        clspath = backend["class"]
        options = backend.get("options", {})
        filters = backend.get("filters", [])

        if isinstance(clspath, str):
            modpath, clsname = split_clspath(clspath)
            try:
                __import__(modpath)
                module = sys.modules[modpath]
                cls = getattr(module, clsname)
            except Exception:
                logger.exception("Exception while importing %s", clspath)
                if raise_errors:
                    raise
                continue
        else:
            cls = clspath

        try:
            good_backends.append(cls(options=options, filters=filters))
        except Exception:
            logger.exception(
                "Exception thrown while instantiating %s, %s", clspath, options
            )
            if raise_errors:
                raise

    _change_metrics(good_backends)


class MetricsRecord:
    """Record for a single emitted metric.

    :attribute stat_type: the type of the stat ('incr', 'gauge', 'timing',
        'histogram')
    :attribute key: the full key for this record
    :attribute value: the value for this record
    :attribute tags: list of tag strings

    """

    def __init__(self, stat_type, key, value, tags):
        self.stat_type = stat_type
        self.key = key
        self.value = value
        self.tags = tags or []

    def __repr__(self):
        return "<MetricsRecord %r %r %r %r>" % (
            self.stat_type,
            self.key,
            self.value,
            self.tags,
        )

    def __copy__(self):
        # NOTE(willkg): the only attribute that's mutable is tags--the rest
        # we can just copy verbatim
        return MetricsRecord(self.stat_type, self.key, self.value, list(self.tags))


class MetricsFilter:
    """Filter class for augmenting metrics.

    Subclass MetricsFilter to build filters that augment metrics as they're
    published.

    """

    def filter(self, record):
        """Filter a record

        You can adjust a record, return the record as-is, or return ``None``
        which will drop the record from publishing.

        Records are :py:class:`markus.main.MetricsRecord`.

        """
        return record


class MetricsInterface:
    """Interface to generating metrics.

    This is the interface to generating metrics. When you call methods on this
    instance, it publishes those metrics to the configured backends.

    In this way, code can get a :py:class:`markus.main.MetricsInterface` at any
    time even before backends have been configured. Further, backends can be
    switched around without affecting existing
    :py:class:`markus.main.MetricsInterface` instancess.

    See :py:func:`markus.get_metrics` for generating
    :py:class:`markus.main.MetricsInterface` instances.

    """

    def __init__(self, prefix, filters=None):
        """Create a MetricsInterface.

        :arg str prefix: Use alphanumeric characters and underscore and period.
            Anything else gets converted to a period. Sequences of periods get
            collapsed to a single period.

            The prefix is prepended to all keys emitted by this metrics
            interface.

        :arg list of MetricsFilter filters: list of filters to apply to
            records being emitted

        """
        # Convert all bad characters to .
        prefix = NOT_ALPHANUM_RE.sub(".", prefix)
        # Collapse sequences of . to a single .
        prefix = CONSECUTIVE_PERIODS_RE.sub(".", prefix)
        # Remove . at beginning and end
        self.prefix = prefix.strip(".")

        self.filters = filters or []

    def __repr__(self):
        return "<MetricsInterface %s %s>" % (self.prefix, repr(self.filters))

    def _full_stat(self, stat):
        if self.prefix:
            return self.prefix + "." + stat
        else:
            return stat

    def _publish(self, record):
        """Publish a record to backends.

        If one of the filters rejects the record, then the record does not get
        published.

        """
        # First run filters configured on the MetricsInterface
        for metrics_filter in self.filters:
            record = metrics_filter.filter(record)
            if record is None:
                return

        for backend in _get_metrics_backends():
            # Copy the record so filtering in one backend doesn't affect other
            # backends
            fresh_record = record.__copy__()
            backend.emit_to_backend(fresh_record)

    def incr(self, stat, value=1, tags=None):
        """Incr is used for counting things.

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: A value to increment the count by. Usually this is 1.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def chop_vegetable(kind):
        ...     # chop chop chop
        ...     metrics.incr('vegetable', value=1)

        You can also use incr to decrement by passing a negative value.

        """
        self._publish(
            MetricsRecord(
                stat_type="incr", key=self._full_stat(stat), value=value, tags=tags
            )
        )

    def gauge(self, stat, value, tags=None):
        """Gauges are used for measuring things.

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: The measured value of the thing being measured.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def parse_payload(payload):
        ...     metrics.gauge('payload_size', value=len(payload))
        ...     # parse parse parse

        """
        self._publish(
            MetricsRecord(
                stat_type="gauge", key=self._full_stat(stat), value=value, tags=tags
            )
        )

    def timing(self, stat, value, tags=None):
        """Record a timing value.

        Record the length of time of something to be added to a set of values from
        which a statistical distribution is derived.

        Depending on the backend, you might end up with count, average, median,
        95% and max for a set of timing values.

        This is useful for analyzing how long things take to occur. For
        example, how long it takes for a function to run, to upload files, or
        for a database query to execute.

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: A timing in milliseconds.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> import time
        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def upload_file(payload):
        ...     start_time = time.perf_counter()  # this is in seconds
        ...     # upload the file
        ...     timing = (time.perf_counter() - start_time) * 1000.0  # convert to ms
        ...     metrics.timing('upload_file_time', value=timing)

        .. Note::

           If you're timing a function or a block of code, it's probably more
           convenient to use :py:meth:`markus.main.MetricsInterface.timer` or
           :py:meth:`markus.main.MetricsInterface.timer_decorator`.

        """
        self._publish(
            MetricsRecord(
                stat_type="timing", key=self._full_stat(stat), value=value, tags=tags
            )
        )

    def histogram(self, stat, value, tags=None):
        """Record a histogram value.

        Record a value to be added to a set of values from which a statistical
        distribution is derived.

        Depending on the backend, you might end up with count, average, median,
        95% and max for a set of values.

        This is useful for analyzing distributions of values. For example,
        what's the median and 95% upload file size? What's the most expensive
        thing sold?

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: The value of the thing.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> import time
        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def finalize_sale(cart):
        ...     for item in cart:
        ...         metrics.histogram('item_cost', value=item.cost)
        ...     # finish finalizing

        .. Note::

           For metrics backends that don't have histogram, this will do the
           same as timing.

        """
        self._publish(
            MetricsRecord(
                stat_type="histogram", key=self._full_stat(stat), value=value, tags=tags
            )
        )

    @contextlib.contextmanager
    def timer(self, stat, tags=None):
        """Contextmanager for easily computing timings.

        :arg string stat: A period delimited alphanumeric key.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> mymetrics = get_metrics(__name__)

        >>> def long_function():
        ...     with mymetrics.timer('long_function'):
        ...         # perform some thing we want to keep metrics on
        ...         pass


        .. Note::

           All timings generated with this are in milliseconds.

        """
        start_time = time.perf_counter()

        yield

        end_time = time.perf_counter()

        delta = end_time - start_time
        self.timing(stat, value=delta * 1000.0, tags=tags)

    def timer_decorator(self, stat, tags=None):
        """Timer decorator for easily computing timings.

        :arg string stat: A period delimited alphanumeric key.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

            To pass no tags, either pass an empty list or ``None``.

        For example:

        >>> mymetrics = get_metrics(__name__)

        >>> @mymetrics.timer_decorator('long_function')
        ... def long_function():
        ...     # perform some thing we want to keep metrics on
        ...     pass


        .. Note::

           All timings generated with this are in milliseconds.

        """

        def _inner(fun):
            @wraps(fun)
            def _timer_decorator(*args, **kwargs):
                with self.timer(stat, tags):
                    return fun(*args, **kwargs)

            return _timer_decorator

        return _inner


def get_metrics(thing="", extra="", filters=None):
    """Return MetricsInterface instance with specified prefix.

    The prefix is prepended to all keys emitted with this
    :py:class:`markus.main.MetricsInterface`.

    The :py:class:`markus.main.MetricsInterface` is not tied to metrics
    backends. The list of active backends are globally configured. This allows
    us to create :py:class:`markus.main.MetricsInterface` classes without
    having to worry about bootstrapping order of the app.

    :arg class/instance/str thing: The prefix to use for keys generated
        with this :py:class:`markus.main.MetricsInterface`.

        If this is a string, then it uses it as a prefix.

        If this is a class, it uses the dotted Python path.

        If this is an instance, it uses the dotted Python path plus
        ``str(instance)``.

    :arg str extra: Any extra bits to add to the end of the prefix.

    :arg list of MetricsFilters filters: any filters to apply to all metrics
        generated using this MetricsInterface

    :returns: a ``MetricsInterface`` instance

    Examples:

    >>> from markus import get_metrics

    Create a MetricsInterface with the prefix "myapp" and generate a count with
    stat "myapp.thing1" and value 1:

    >>> metrics = get_metrics('myapp')
    >>> metrics.incr('thing1', value=1)

    Create a MetricsInterface with the prefix of the Python module it's being
    called in:

    >>> metrics = get_metrics(__name__)

    Create a MetricsInterface with the prefix as the qualname of the class:

    >>> class Foo:
    ...     def __init__(self):
    ...         self.metrics = get_metrics(self)

    Create a prefix of the class path plus some identifying information:

    >>> class Foo:
    ...     def __init__(self, myprefix):
    ...         self.metrics = get_metrics(self, extra=myprefix)
    ...
    >>> foo = Foo('jim')

    Assume that ``Foo`` is defined in the ``myapp`` module. Then this will
    generate the prefix ``myapp.Foo.jim``.

    Create a MetricsFilter and add it to the metrics interface:

    >>> from markus.main import MetricsFilter
    >>> class BlueTagFilter(MetricsFilter):
    ...     def filter(self, record):
    ...         record.tags.append('color:blue')
    ...         return record
    ...
    >>> metrics = get_metrics('foo', filters=[BlueTagFilter()])

    """
    thing = thing or ""

    if not isinstance(thing, str):
        # If it's not a str, it's either a class or an instance. Handle
        # accordingly.
        if type(thing) == type:
            thing = "%s.%s" % (thing.__module__, thing.__name__)
        else:
            thing = "%s.%s" % (thing.__class__.__module__, thing.__class__.__name__)

    if extra:
        thing = "%s.%s" % (thing, extra)

    return MetricsInterface(thing, filters=filters)
