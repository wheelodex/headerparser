from .errors import HeaderTypeError

TRUTHY = set(['yes', 'y', 'on',  'true',  '1'])
FALSEY = set(['no',  'n', 'off', 'false', '0'])

def BOOL(s):
    if isinstance(s, bool):  # In case BOOL is somehow applied twice
        return s
    b = s.strip().lower()
    if b in TRUTHY:
        return True
    elif b in FALSEY:
        return False
    else:
        raise HeaderTypeError('BOOL', s)
