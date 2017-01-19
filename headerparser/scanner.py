from .errors import MalformedHeaderError, UnexpectedFoldingError
from .util   import ascii_splitlines

# The functions return a generator of (header_name, header_value) pairs in
# which the body is represented as a "header" with a name of `None`

# For header values other than the body, trailing line endings are removed,
# and embedded line endings are converted to \n

# A body item is only returned if the headers are terminated by a blank line
# rather than EOF

def scan_string(s):
    lineiter = iter(ascii_splitlines(s, True))
    return _scan_lines(lineiter)

def scan_file(fp):
    return _scan_lines(fp)

def _scan_lines(lineiter):
    name  = None
    value = ''
    eof   = False
    for line in lineiter:
        line = line.rstrip('\r\n')
        if line.startswith((' ', '\t')):
            if name is not None:
                value += '\n' + line
            else:
                raise UnexpectedFoldingError  ### TODO
        elif ':' in line:
            if name is not None:
                yield (name, value)
            name, _, value = line.partition(':')
            name = name.rstrip(' \t')  ### ???
            value = value.lstrip(' \t')
        elif line == '':
            break
        else:
            raise MalformedHeaderError  ### TODO
    else:
        eof = True
    if name is not None:
        yield (name, value)
    if not eof:
        yield (None, ''.join(lineiter))
