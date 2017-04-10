# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import contextlib
from functools import wraps
import logging
import re
import sys
import time


NOT_ALPHANUM_RE = re.compile(r'[^a-z0-9_\.]', re.I)


logger = logging.getLogger(__name__)


_metrics_backends = []


def _change_metrics(backends):
    """Convenience function for setting backends"""
    global _metrics_backends
    _metrics_backends = backends


def _get_metrics_backends():
    return _metrics_backends


def split_clspath(clspath):
    """Simple split of clspath into a module and class name

    NOTE(willkg): This is really simple. Maybe we should use something more
    sophisticated?

    """
    return clspath.rsplit('.', 1)


def configure(backends):
    """Instantiates and configures backends

    :arg list-of-dicts backends: the backend configuration as a list of dicts where
        each dict specifies a separate backend.

        Each backend consists of a ``class`` and an ``options`` dict that is
        passed into the backend class when instantiated to configure it.

        See the documentation for the backends you're using to know what
        is configurable in the options dict.


    For example, this sets up a
    :py:class:`markus.backends.logging.LoggingMetrics` backend::

        markus.configure([
            {
                'class': 'markus.backends.logging.LoggingMetrics',
                'options': {
                    'logger_name': 'metrics'
                }
            }
        ])


    You can set up as many backends as you like.

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
        clspath = backend['class']
        options = backend.get('options', {})

        modpath, clsname = split_clspath(clspath)
        try:
            __import__(modpath)
            module = sys.modules[modpath]
            cls = getattr(module, clsname)
        except Exception:
            logger.exception('Exception while importing %s', clspath)
            continue

        try:
            good_backends.append(cls(options))
        except Exception:
            logger.exception(
                'Exception thrown while instantiating %s, %s',
                clspath,
                options
            )

    _change_metrics(good_backends)


class MetricsInterface:
    """Interface to generating metrics

    This is the interface to generating metrics. When you call methods on this
    instance, it publishes those metrics to the configured backends.

    In this way, code can get a :py:class:`markus.main.MetricsInterface` at any
    time even before backends have been configured. Further, backends can be
    switched around without affecting existing
    :py:class:`markus.main.MetricsInterface` instancess.

    See :py:func:`markus.get_metrics` for generating
    :py:class:`markus.main.MetricsInterface` instances.

    """
    def __init__(self, name):
        """Creates a MetricsInterface

        :arg str name: Use alphanumeric characters and underscore and period.
            Anything else gets converted to a period. Sequences of periods get
            collapsed to a single period.

        """
        # Convert all bad characters to .
        name = NOT_ALPHANUM_RE.sub('.', name)
        # Collapse sequences of . to a single .
        while True:
            new_name = name.replace('..', '.')
            if new_name == name:
                break
            name = new_name
        # Remove . at beginning and end
        self.name = name.strip('.')

    def _full_stat(self, stat):
        if self.name:
            return self.name + '.' + stat
        else:
            return stat

    def incr(self, stat, value=1, tags=None):
        """Incr is used for counting things

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: A value to increment the count by. Usually this is 1.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

        For example:

        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def chop_vegetable(kind):
        ...     # chop chop chop
        ...     metrics.incr('vegetable', value=1)

        You can also use incr to decrement by passing a negative value.

        """
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.incr(full_stat, value=value, tags=tags)

    def gauge(self, stat, value, tags=None):
        """Gauges are used for measuring things

        :arg string stat: A period delimited alphanumeric key.

        :arg int value: The measured value of the thing being measured.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

        For example:

        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def parse_payload(payload):
        ...     metrics.gauge('payload_size', value=len(payload))
        ...     # parse parse parse

        """
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.gauge(full_stat, value=value, tags=tags)

    def timing(self, stat, value, tags=None):
        """Record the length of time of something to be added to a set of values from
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

        For example:

        >>> import time
        >>> import markus

        >>> metrics = markus.get_metrics('foo')
        >>> def upload_file(payload):
        ...     start_time = time.time()  # this is in seconds
        ...     # upload the file
        ...     timing = (time.time() - start_time) * 1000.0  # convert to ms
        ...     metrics.timing('upload_file_time', value=timing)

        .. Note::

           If you're timing a function or a block of code, it's probably more
           convenient to use :py:meth:`markus.main.MetricsInterface.timer` or
           :py:meth:`markus.main.MetricsInterface.timer_decorator`.

        """
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.timing(full_stat, value=value, tags=tags)

    def histogram(self, stat, value, tags=None):
        """Record a value to be added to a set of values from which a statistical
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
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.histogram(full_stat, value=value, tags=tags)

    @contextlib.contextmanager
    def timer(self, stat, tags=None):
        """Contextmanager for easily computing timings

        :arg string stat: A period delimited alphanumeric key.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

        For example:

        >>> mymetrics = get_metrics(__name__)

        >>> def long_function():
        ...     with mymetrics.timer('long_function'):
        ...         # perform some thing we want to keep metrics on
        ...         pass

        """
        start_time = time.time()
        yield
        delta = time.time() - start_time
        self.timing(stat, value=delta * 1000.0, tags=tags)

    def timer_decorator(self, stat, tags=None):
        """Timer decorator for easily computing timings

        :arg string stat: A period delimited alphanumeric key.

        :arg list-of-strings tags: Each string in the tag consists of a key and
            a value separated by a colon. Tags can make it easier to break down
            metrics for analysis.

            For example ``['env:stage', 'compressed:yes']``.

        For example:

        >>> mymetrics = get_metrics(__name__)

        >>> @mymetrics.timer_decorator('long_function')
        ... def long_function():
        ...     # perform some thing we want to keep metrics on
        ...     pass

        """
        def _inner(fun):
            @wraps(fun)
            def _timer_decorator(*args, **kwargs):
                with self.timer(stat, tags):
                    return fun(*args, **kwargs)
            return _timer_decorator
        return _inner


def get_metrics(thing, extra=''):
    """Return a :py:class:`markus.main.MetricsInterface` instance with specified name

    The name is used as the prefix for all keys generated with this
    :py:class:`markus.main.MetricsInterface`.

    The :py:class:`markus.main.MetricsInterface` is not tied to metrics
    backends. The list of active backends are globally configured. This allows
    us to create :py:class:`markus.main.MetricsInterface` classes without
    having to worry about bootstrapping order of the app.

    :arg class/instance/str thing: The name to use as a key prefix.

        If this is a class, it uses the dotted Python path. If this is an
        instance, it uses the dotted Python path plus ``str(instance)``.

    :arg str extra: Any extra bits to add to the end of the name.

    :returns: a ``MetricsInterface`` instance

    Examples:

    >>> from markus import get_metrics

    Create a MetricsInterface with the name "myapp" and generate a count with
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
    ...     def __init__(self, myname):
    ...         self.metrics = get_metrics(self, extra=myname)
    ...
    >>> foo = Foo('jim')

    Assume that ``Foo`` is defined in the ``myapp`` module. Then this will
    generate the name ``myapp.Foo.jim``.

    """
    thing = thing or ''

    if not isinstance(thing, str):
        # If it's not a str, it's either a class or an instance. Handle
        # accordingly.
        if type(thing) == type:
            thing = '%s.%s' % (thing.__module__, thing.__name__)
        else:
            thing = '%s.%s' % (
                thing.__class__.__module__, thing.__class__.__name__
            )

    if extra:
        thing = '%s.%s' % (thing, extra)

    return MetricsInterface(thing)
