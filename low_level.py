def lex822(s):
    # Returns a generator of (header_name, header_value) pairs in which the
    # body is represented as a "header" with a name of `None`
    ### TODO: Add a variant that takes a filehandle
    name = None
    value = ''
    lineiter = iter(ascii_splitlines(s, True))
    for line in lineiter:
        if line.startswith((' ', '\t')):
            if name is not None:
                value += line
            else:
                raise ValueError ###
        elif ':' in line:
            if name is not None:
                yield (name, value)
            name, _, value = line.partition(':')
            name = name.rstrip(' \t')  ### ???
            value = value.lstrip(' \t')
        elif line.rstrip('\r\n') == '':
            break
        else:
            raise ValueError ###
    else:
        if name is not None:
            yield (name, value)
    if name is not None:
        yield (name, value)
    yield (None, ''.join(lineiter))

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
