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
    """Instantiates and configures the metrics implementation"""
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

    This is the interface to publishing metrics. When you call methods on this
    instance, it calls the appropriate methods on the configured backends.

    In this way, code can get a :py:class:`markus.main.MetricsInterface` at any
    time even before backends have been configured. Further, backends can be
    switched around without affecting existing
    :py:class:`markus.main.MetricsInterface` instancess.

    For example, at the top of your Python module, you could have this::

        import markus

        mymetrics = markus.get_metrics(__name__)


    If that Python module was imported with ``antenna.app``, then that'd be the
    first part of all stats published by that metrics interface instance.

    Maybe you want instance-specific metrics. You could define a class and have
    it get a metrics in the init::

        class SomeClass:
            def __init__(self):
                self.mymetrics = markus.get_metrics(self)


    Any use of ``self.mymetrics`` would emit stats that start with
    ``antenna.app.SomeClass``.

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

    def incr(self, stat, value=1, **extra):
        """Increment a stat by value"""
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.incr(full_stat, value=value, **extra)

    def gauge(self, stat, value, **extra):
        """Set a gauge stat as value"""
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.gauge(full_stat, value=value, **extra)

    def timing(self, stat, value, **extra):
        """Send timing information

        .. Note::

           value is in ms.

        """
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.timing(full_stat, value=value, **extra)

    def histogram(self, stat, value, **extra):
        """Send data information which gets rolled as a histogram

        .. Note::

           For metrics systems that don't have histogram, this will do the same
           as timing.

        """
        full_stat = self._full_stat(stat)
        for backend in _metrics_backends:
            backend.histogram(full_stat, value=value, **extra)

    @contextlib.contextmanager
    def timer(self, stat):
        """Contextmanager for easily computing timings

        For example::

            mymetrics = get_metrics(__name__)

            def long_function():
                with mymetrics.timer('long_function'):
                    # perform some thing we want to keep metrics on
                    ...

        """
        start_time = time.time()
        yield
        delta = time.time() - start_time
        self.timing(stat, delta * 1000.0)

    def timer_decorator(self, stat):
        """Timer decorator for easily computing timings

        For example::

            mymetrics = get_metrics(__name__)

            @mymetrics.timer_decorator('long_function')
            def long_function():
                # perform some thing we want to keep metrics on
                ...

        """
        def _inner(fun):
            @wraps(fun)
            def _timer_decorator(*args, **kwargs):
                with self.timer(stat):
                    return fun(*args, **kwargs)
            return _timer_decorator
        return _inner


def get_metrics(thing, extra=''):
    """Return a MetricsInterface instance with specified name

    Note: This is not tied to an actual metrics implementation. The
    implementation is globally configured. This allows us to have module-level
    variables without having to worry about bootstrapping order.

    :arg class/instance/str thing: The name to use as a key prefix.

        If this is a class, it uses the dotted Python path. If this is an
        instance, it uses the dotted Python path plus ``str(instance)``.

    :arg str extra: Any extra bits to add to the end of the name.

    :returns: a ``MetricsInterface`` instance

    Examples:

    >>> from markus import get_metrics

    Create a MetricsInterface with the prefix "myapp":

    >>> metrics = get_metrics('myapp')
    >>> metrics.incr('thing1', value=1)

    Create a MetricsInterface with the prefix of the Python module:

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
    >>> foo.metrics.name
    'markus.main.Foo.jim'

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
