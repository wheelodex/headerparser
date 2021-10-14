import re
from typing import Iterable, Iterator, List, Optional, Pattern, Tuple, Union
from .errors import MalformedHeaderError, UnexpectedFoldingError
from .util import ascii_splitlines

RgxType = Union[str, "Pattern[str]"]

FieldType = Tuple[Optional[str], str]

DEFAULT_SEPARATOR_REGEX = re.compile(r"[ \t]*:[ \t]*")


def scan_string(
    s: str,
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Iterator[FieldType]:
    """
    Scan a string for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan()` for more information on the exact behavior of the scanner.

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan()`
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return scan(
        ascii_splitlines(s),
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    )


def scan(
    iterable: Iterable[str],
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Iterator[FieldType]:
    """
    .. versionadded:: 0.4.0

    Scan a text-file-like object or iterable of lines for RFC 822-style header
    fields and return a generator of ``(name, value)`` pairs for each header
    field in the input, plus a ``(None, body)`` pair representing the body (if
    any) after the header section.

    All lines after the first blank line are concatenated & yielded as-is in a
    ``(None, body)`` pair.  (Note that body lines which do not end with a line
    terminator will not have one appended.)  If there is no empty line in
    ``iterable``, then no body pair is yielded.  If the empty line is the last
    line in ``iterable``, the body will be the empty string.  If the empty line
    is the *first* line in ``iterable`` and the ``skip_leading_newlines``
    option is false (the default), then all other lines will be treated as part
    of the body and will not be scanned for header fields.

    :param iterable: a text-file-like object or iterable of strings
        representing lines of input
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    lineiter = iter(iterable)
    for name, value in _scan_next_stanza(
        lineiter,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    ):
        if name is not None:
            yield (name, value)
        elif value:
            yield (None, "".join(lineiter))


def scan_next_stanza(
    iterator: Iterable[str],
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Iterator[Tuple[str, str]]:
    """
    .. versionadded:: 0.4.0

    Scan a text-file-like object or iterator of lines for RFC 822-style header
    fields and return a generator of ``(name, value)`` pairs for each header
    field in the input.  Input processing stops as soon as a blank line is
    encountered, leaving the rest of the iterator unconsumed (If
    ``skip_leading_newlines`` is true, the function only stops on a blank line
    after a non-blank line).

    :param iterator: a text-file-like object or iterator of strings
        representing lines of input
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    for name, value in _scan_next_stanza(
        iterator,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    ):
        if name is not None:
            yield (name, value)


def _scan_next_stanza(
    iterator: Iterable[str],
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
):
    """
    .. versionadded:: 0.4.0

    Like `scan_next_stanza()`, except it additionally yields as its last item a
    ``(None, flag)`` pair where ``flag`` is `True` iff the stanza was
    terminated by a blank line (thereby suggesting there is more input left to
    process), `False` iff the stanza was terminated by EOF.

    This is the core function that all other scanners ultimately call.
    """
    name = None
    value = ""
    begun = False
    more_left = False
    if separator_regex is None:
        sep = DEFAULT_SEPARATOR_REGEX
    else:
        sep = re.compile(separator_regex)
    for line in iterator:
        line = line.rstrip("\r\n")
        if line.startswith((" ", "\t")):
            begun = True
            if name is not None:
                value += "\n" + line
            else:
                raise UnexpectedFoldingError(line)
        else:
            m = sep.search(line)
            if m:
                begun = True
                if name is not None:
                    yield (name, value)
                name = line[: m.start()]
                value = line[m.end() :]
            elif line == "":
                if skip_leading_newlines and not begun:
                    continue
                else:
                    more_left = True
                    break
            else:
                raise MalformedHeaderError(line)
    if name is not None:
        yield (name, value)
    yield (None, more_left)


def scan_next_stanza_string(
    s: str,
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Tuple[List[Tuple[str, str]], str]:
    """
    .. versionadded:: 0.4.0

    Scan a string for RFC 822-style header fields and return a pair ``(fields,
    extra)`` where ``fields`` is a list of ``(name, value)`` pairs for each
    header field in the input up to the first blank line and ``extra`` is
    everything after the first blank line (If ``skip_leading_newlines`` is
    true, the dividing point is instead the first blank line after a non-blank
    line); if there is no appropriate blank line in the input, ``extra`` is the
    empty string.

    :param s: a string to scan
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: pair of a list of pairs of strings and a string
    :raises ScannerError: if the header section is malformed
    """
    lineiter = iter(ascii_splitlines(s))
    fields = list(
        scan_next_stanza(
            lineiter,
            separator_regex=separator_regex,
            skip_leading_newlines=skip_leading_newlines,
        )
    )
    body = "".join(lineiter)
    return (fields, body)


def scan_stanzas(
    iterable: Iterable[str],
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Iterator[List[Tuple[str, str]]]:
    """
    .. versionadded:: 0.4.0

    Scan a text-file-like object or iterable of lines for zero or more stanzas
    of RFC 822-style header fields and return a generator of lists of ``(name,
    value)`` pairs, where each list represents a stanza of header fields in the
    input.

    The stanzas are terminated by blank lines.  Consecutive blank lines between
    stanzas are treated as a single blank line.  Blank lines at the end of the
    input are discarded without creating a new stanza.

    :param iterable: a text-file-like object or iterable of strings
        representing lines of input
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of lists of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    lineiter = iter(iterable)
    while True:
        fields = list(
            _scan_next_stanza(
                lineiter,
                separator_regex=separator_regex,
                skip_leading_newlines=skip_leading_newlines,
            )
        )
        more_left = fields.pop()[1]
        if fields or more_left:
            yield fields
        else:
            break
        skip_leading_newlines = True


def scan_stanzas_string(
    s: str,
    separator_regex: Optional[RgxType] = None,
    skip_leading_newlines: bool = False,
) -> Iterator[List[Tuple[str, str]]]:
    """
    .. versionadded:: 0.4.0

    Scan a string for zero or more stanzas of RFC 822-style header fields and
    return a generator of lists of ``(name, value)`` pairs, where each list
    represents a stanza of header fields in the input.

    The stanzas are terminated by blank lines.  Consecutive blank lines between
    stanzas are treated as a single blank line.  Blank lines at the end of the
    input are discarded without creating a new stanza.

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan_stanzas()`
    :param kwargs: :ref:`scanner options <scan_opts>`
    :rtype: generator of lists of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return scan_stanzas(
        ascii_splitlines(s),
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    )
