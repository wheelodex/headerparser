import re
from   warnings import warn
from   .errors  import MalformedHeaderError, UnexpectedFoldingError
from   .util    import ascii_splitlines

def scan_string(s, **kwargs):
    """
    Scan a string for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan()` for more information on the exact behavior of the scanner.

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan()`
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    return scan(ascii_splitlines(s), **kwargs)

def scan_file(fp, **kwargs):
    """
    Scan a file for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan()` for more information on the exact behavior of the scanner.

    .. deprecated:: 0.4.0
        Use `scan()` instead.

    :param fp: A file-like object than can be iterated over to produce lines to
        pass to `scan()`.  Opening the file in universal newlines mode is
        recommended.
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    warn('scan_file() is deprecated.  Use scan() instead.', DeprecationWarning)
    return scan(fp, **kwargs)

def scan_lines(fp, **kwargs):
    """
    Scan an iterable of lines for RFC 822-style header fields and return a
    generator of ``(name, value)`` pairs for each header field in the input,
    plus a ``(None, body)`` pair representing the body (if any) after the
    header section.

    See `scan()` for more information on the exact behavior of the scanner.

    .. deprecated:: 0.4.0
        Use `scan()` instead.

    :param iterable: an iterable of strings representing lines of input
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """
    warn('scan_lines() is deprecated.  Use scan() instead.', DeprecationWarning)
    return scan(fp, **kwargs)

def scan(
    iterable,
    separator_regex       = re.compile(r'[ \t]*:[ \t]*'),
    skip_leading_newlines = False,
):
    """
    .. versionadded:: 0.4.0

    Scan a text-file-like object or iterable of lines for RFC 822-style header
    fields and return a generator of ``(name, value)`` pairs for each header
    field in the input, plus a ``(None, body)`` pair representing the body (if
    any) after the header section.

    Each field value is a single string, the concatenation of one or more
    lines, with leading whitespace on lines after the first preserved.  The
    ending of each line is converted to ``'\\n'`` (added if there is no
    ending), and the last line of the field value has its trailing line ending
    (if any) removed.

    .. note::

        "Line ending" here means a CR, LF, or CR LF sequence at the end of one
        of the lines in ``iterable``.  Unicode line separators, along with line
        endings occurring in the middle of a line, are not treated as line
        endings and are not trimmed or converted to ``\\n``.

    All lines after the first blank line are concatenated & yielded as-is in a
    ``(None, body)`` pair.  (Note that body lines which do not end with a line
    terminator will not have one appended.)  If there is no empty line in
    ``iterable``, then no body pair is yielded.  If the empty line is the last
    line in ``iterable``, the body will be the empty string.  If the empty line
    is the *first* line in ``iterable`` and the ``skip_leading_newlines``
    option is `False` (the default), then all other lines will be treated as
    part of the body and will not be scanned for header fields.

    :param iterable: a text-file-like object or iterable of strings
        representing lines of input
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises MalformedHeaderError: if an invalid header line, i.e., a line
        without either a colon or leading whitespace, is encountered
    :raises UnexpectedFoldingError: if a folded (indented) line that is not
        preceded by a valid header line is encountered
    """

    lineiter = iter(iterable)
    name  = None
    value = ''
    eof   = False
    begun = False
    if not hasattr(separator_regex, 'match'):
        separator_regex = re.compile(separator_regex)
    for line in lineiter:
        line = line.rstrip('\r\n')
        if line.startswith((' ', '\t')):
            begun = True
            if name is not None:
                value += '\n' + line
            else:
                raise UnexpectedFoldingError(line)
        else:
            m = separator_regex.search(line)
            if m:
                begun = True
                if name is not None:
                    yield (name, value)
                name = line[:m.start()]
                value = line[m.end():]
            elif line == '':
                if skip_leading_newlines and not begun:
                    continue
                else:
                    break
            else:
                raise MalformedHeaderError(line)
    else:
        eof = True
    if name is not None:
        yield (name, value)
    if not eof:
        yield (None, ''.join(lineiter))
