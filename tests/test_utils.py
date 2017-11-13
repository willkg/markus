# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from markus.utils import generate_tag


@pytest.mark.parametrize('key, value, expected', [
    ('', None, ''),
    ('', '', ''),
    ('a', None, 'a'),

    # Key and value are concatenated using :
    ('a', 'b', 'a:b'),

    # First character must be a letter
    ('1', None, 'a1'),

    # Test good characters
    ('abcdefghijklmnopqrstuvwxyz0123456789-_/.', None, 'abcdefghijklmnopqrstuvwxyz0123456789-_/.'),

    # Ok with unicode
    (u'joe\u018Ajoe', None, u'joe_joe'),

    # Test bad characters get converted to _
    ('a&b', None, 'a_b'),
    ('email', 'foo@example.com', 'email:foo_example.com'),

    # Tags are lowercased
    ('ABC', 'DEF', 'abc:def'),

    # Long tags are truncated to 200 characters
    ('a' * 201, None, 'a' * 200),

    # device host, and source all get "_" appended to the end
    ('device', None, 'device_'),
    ('host', None, 'host_'),
    ('source', None, 'source_'),
])
def test_generate_tag(key, value, expected):
    assert generate_tag(key, value) == expected


def test_generate_tag_bad_data():
    with pytest.raises(ValueError) as exc_info:
        generate_tag(42)

    assert str(exc_info.value) == 'key must be a string type, but got 42 instead'

    with pytest.raises(ValueError) as exc_info:
        generate_tag('key', 42)

    assert str(exc_info.value) == 'value must be None or a string type, but got 42 instead'
