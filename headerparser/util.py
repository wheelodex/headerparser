import re

def unfold(s):
    return s.replace('\r', '').replace('\n', '')

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
