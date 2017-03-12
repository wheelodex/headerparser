from   operator import methodcaller

lower = methodcaller('lower')

TRUTHY = {'yes', 'y', 'on',  'true',  '1'}
FALSEY = {'no',  'n', 'off', 'false', '0'}

def BOOL(s):
    """
    Convert boolean-like strings to `bool` values.  The strings ``'yes'``,
    ``'y'``, ``'on'``, ``'true'``, and ``'1'`` are converted to `True`, and the
    strings ``'no'``, ``'n'``, ``'off'``, ``'false'``, and ``'0'`` are
    converted to `False`.  The conversion is case-insensitive and ignores
    leading & trailing whitespace.  Any value that cannot be converted to a
    `bool` results in a `ValueError`.

    :param string s: a boolean-like string to convert to a `bool`
    :rtype: bool
    :raises ValueError: if ``s`` is not one of the values listed above
    """
    b = s.strip().lower()
    if b in TRUTHY:
        return True
    elif b in FALSEY:
        return False
    else:
        raise ValueError('invalid boolean: ' + repr(s))
