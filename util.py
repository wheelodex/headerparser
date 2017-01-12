def unfold(s):
    return s.replace('\r', '').replace('\n', '')

TRUTHY = {'yes', 'y', 'on',  'true',  '1'}
FALSEY = {'no',  'n', 'off', 'false', '0'}

def parse_bool(s):
    if isinstance(s, bool):
        return s
    s = s.strip().lower()
    if s in TRUTHY:
        return True
    elif s in FALSEY:
        return False
    else:
        raise ValueError ###
