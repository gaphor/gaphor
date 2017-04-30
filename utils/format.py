from __future__ import absolute_import
import re

pattern = r'([A-Z])'
sub = r'_\1'


def camelCase_to_underscore(str):
    """
    >>> camelCase_to_underscore('camelcase')
    'camelcase'
    >>> camelCase_to_underscore('camelCase')
    'camel_case'
    >>> camelCase_to_underscore('camelCamelCase')
    'camel_camel_case'
    """
    return re.sub(pattern, sub, str).lower()


if __name__ == '__main__':
    import doctest

    doctest.testmod()
