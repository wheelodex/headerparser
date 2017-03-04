from .errors import MalformedHeaderError, UnexpectedFoldingError
from .util   import ascii_splitlines

def scan_string(s):
    """
    Scan a string for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan_lines()` for more information on the exact behavior of the
    scanner.

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan_lines()`
    :return: a generator of ``(name, value)`` pairs
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    return scan_lines(ascii_splitlines(s, True))

def scan_file(fp):
    """
    Scan a file for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan_lines()` for more information on the exact behavior of the
    scanner.

    :param fp: A file-like object than can be iterated over to produce lines to
        pass to `scan_lines()`.  Opening the file in universal newlines mode is
        recommended.
    :return: a generator of ``(name, value)`` pairs
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    ### TODO: Handle files not opened in universal newlines mode?
    return scan_lines(fp)

def scan_lines(iterable):
    """
    Scan an iterable of lines for RFC 822-style header fields and return a
    generator of ``(name, value)`` pairs for each header field in the input,
    plus a ``(None, body)`` pair representing the body (if any) after the
    header section.

    The input is assumed to consist of at most two parts: a header section,
    containing zero or more header fields, and an optional free-form body,
    which (if present) is separated from the header section by an empty line.

    An individual header field consists of one or more lines, with all lines
    other than the first beginning with a space or tab.  Additionally, the
    first line must contain a colon (optionally surrounded by whitespace)
    separating the field name from the first line of the field value.  The
    first line of the field value is then concatenated with the remaining lines
    of the header field (with leading whitespace preserved) to produce the
    complete field value.  Line endings in the field value are converted to
    ``\\n``, and a trailing line ending (if any) at the end of the field value
    is removed.

    .. note::

        "Line ending" here means a CR, LF, or CR LF sequence at the end of one
        of the lines in ``iterable``.  Unicode line separators, along with line
        endings occurring in the middle of a line, are not treated as line
        endings and are not trimmed or converted to ``\\n``.  Additionally, a
        ``\\n`` is appended to any header field line which does not already end
        in CR, LF, or CR LF.

    An "empty" line containing only a line ending (if anything) denotes the end
    of the header section and the beginning of the body.  All lines after it
    are concatenated & yielded as-is in a ``(None, body)`` pair.

    Note that if there is no empty line in ``iterable``, then no body pair is
    yielded.  If the empty line is the last line in ``iterable``, the body will
    be the empty string.  If the empty line is the *first* line in
    ``iterable``, then all other lines will be treated as part of the body and
    will not be scanned for header fields.

    :param iterable: an iterable of strings representing lines of input, with
        terminating newlines retained
    :return: a generator of ``(name, value)`` pairs
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    lineiter = iter(iterable)
    name  = None
    value = ''
    eof   = False
    for line in lineiter:
        line = line.rstrip('\r\n')
        if line.startswith((' ', '\t')):
            if name is not None:
                value += '\n' + line
            else:
                raise UnexpectedFoldingError(line)
        elif ':' in line:
            if name is not None:
                yield (name, value)
            name, _, value = line.partition(':')
            name = name.rstrip(' \t')
            value = value.lstrip(' \t')
        elif line == '':
            break
        else:
            raise MalformedHeaderError(line)
    else:
        eof = True
    if name is not None:
        yield (name, value)
    if not eof:
        yield (None, ''.join(lineiter))
