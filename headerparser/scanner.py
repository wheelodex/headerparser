from .util import ascii_splitlines

def scan_string(s):
    # Returns a generator of (header_name, header_value) pairs in which the
    # body is represented as a "header" with a name of `None`
    ### TODO: Add a variant that takes a filehandle
    name = None
    value = ''
    lineiter = iter(ascii_splitlines(s, True))
    for line in lineiter:
        line = line.rstrip('\r\n')
        if line.startswith((' ', '\t')):
            if name is not None:
                value += '\n' + line
            else:
                raise ValueError ###
        elif ':' in line:
            if name is not None:
                yield (name, value)
            name, _, value = line.partition(':')
            name = name.rstrip(' \t')  ### ???
            value = value.lstrip(' \t')
        elif line == '':
            break
        else:
            raise ValueError ###
    if name is not None:
        yield (name, value)
    yield (None, ''.join(lineiter))
