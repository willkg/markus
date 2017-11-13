# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

import six


NONE_TYPE = type(None)

# regexp that matches characters that can't be in tags
BAD_TAG_CHAR_REGEXP = re.compile(r'[^0-9a-zA-Z\._\-/]')


def generate_tag(key, value=None):
    """Generates a tag for use with the tag backends

    The key and value (if there is one) are sanitized according to the
    following rules:

    1. after the first character, all characters must be alphanumeric,
       underscore, minus, period, or slash--invalid characters are converted
       to "_"
    2. lowercase

    If a value is provided, the final tag is `key:value`.

    The final tag must start with a letter. If it doesn't, an "a" is prepended.

    The final tag is truncated to 200 characters.

    If the final tag is "device", "host", or "source", then a "_" will be
    appended the end.

    :arg str key: the key to use
    :arg str value: the value (if any)

    :returns: the final tag

    Examples:

    >>> generate_tag('yellow')
    'yellow'
    >>> generate_tag('rule', 'is_yellow')
    'rule:is_yellow'

    Example with ``incr``:

    >>> import markus
    >>> mymetrics = markus.get_metrics(__name__)

    >>> mymetrics.incr('somekey', value=1,
    ...                tags=[generate_tag('rule', 'is_yellow')])

    """
    # Verify the types
    if not isinstance(key, six.string_types):
        raise ValueError('key must be a string type, but got %r instead' % key)

    if not isinstance(value, six.string_types + (NONE_TYPE,)):
        raise ValueError('value must be None or a string type, but got %r instead' % value)

    # Sanitize the key
    key = BAD_TAG_CHAR_REGEXP.sub('_', key).strip()

    # Build the tag
    if value is None or not value.strip():
        tag = key
    else:
        value = BAD_TAG_CHAR_REGEXP.sub('_', value).strip()
        tag = '%s:%s' % (key, value)

    if tag and not tag[0].isalpha():
        tag = 'a' + tag

    # Lowercase and truncate
    tag = tag.lower()[:200]

    # Add _ if it's a reserved word
    if tag in ['device', 'host', 'source']:
        tag = tag + '_'

    return tag
