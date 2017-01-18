import re

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

def ascii_splitlines(s, keepends=False):
    lines = []
    lastend = 0
    for m in re.finditer(r'\r\n?|\n', s):
        if keepends:
            lines.append(s[lastend:m.end()])
        else:
            lines.append(s[lastend:m.start()])
        lastend = m.end()
    if lastend < len(s):
        lines.append(s[lastend:])
    return lines
