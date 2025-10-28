from __future__ import annotations
from collections.abc import Iterable, Iterator
import re
from typing import TypeAlias
import attr
from deprecated import deprecated
from .errors import MalformedHeaderError, ScannerEOFError, UnexpectedFoldingError
from .util import ascii_splitlines

RgxType: TypeAlias = str | re.Pattern[str]

FieldType: TypeAlias = tuple[str | None, str]

DEFAULT_SEPARATOR_REGEX = re.compile(r"[ \t]*:[ \t]*")


def data2iter(data: str | Iterable[str]) -> Iterator[str]:
    if isinstance(data, str):
        data = ascii_splitlines(data)
    return iter(data)


def convert_sep(v: RgxType | None) -> re.Pattern[str]:
    if v is None:
        return DEFAULT_SEPARATOR_REGEX
    else:
        return re.compile(v)


def none2false(v: bool | None) -> bool:
    return False if v is None else v


@attr.define
class Scanner:
    """
    .. versionadded:: 0.5.0

    A class for scanning text for RFC 822-style header fields.  Each method
    processes some portion of the input yet unscanned; the `scan()`,
    `scan_stanzas()`, and `get_unscanned()` methods process the entirety of the
    remaining input, while the `scan_next_stanza()` method only processes up
    through the first blank line.

    :param data:
        The text to scan.  This may be a string, a text-file-like object, or an
        iterable of lines.  If it is a string, it will be broken into lines on
        CR, LF, and CR LF boundaries.

    :param separator_regex:
        A regex (as a `str` or compiled regex object) defining the name-value
        separator; defaults to :regexp:`[ \\\\t]*:[ \\\\t]*`.  When the regex
        is found in a line, everything before the matched substring becomes the
        field name, and everything after becomes the first line of the field
        value.  Note that the regex must match any surrounding whitespace in
        order for it to be trimmed from the key & value.

    :param bool skip_leading_newlines:
        If `True`, blank lines at the beginning of the input will be discarded.
        If `False`, a blank line at the beginning of the input marks the end of
        an empty header section.
    """

    _data: Iterator[str] = attr.field(converter=data2iter)
    separator_regex: re.Pattern[str] = attr.field(
        default=DEFAULT_SEPARATOR_REGEX,
        converter=convert_sep,
        kw_only=True,
    )
    skip_leading_newlines: bool = attr.field(
        default=False, kw_only=True, converter=none2false
    )
    _eof: bool = attr.field(default=False, init=False)

    def scan(self) -> Iterator[FieldType]:
        """
        Scan the remaining input for RFC 822-style header fields and return a
        generator of ``(name, value)`` pairs for each header field encountered,
        plus a ``(None, body)`` pair representing the body (if any) after the
        header section.

        All lines after the first blank line are concatenated & yielded as-is
        in a ``(None, body)`` pair.  (Note that body lines which do not end
        with a line terminator will not have one appended.)  If there is no
        empty line in the input, then no body pair is yielded.  If the empty
        line is the last line in the input, the body will be the empty string.
        If the empty line is the *first* line in the input and the
        ``skip_leading_newlines`` option is false (the default), then all other
        lines will be treated as part of the body and will not be scanned for
        header fields.

        :raises ScannerError: if the header section is malformed
        :raises ScannerEOFError: if all of the input has already been consumed
        """
        yield from self.scan_next_stanza()
        try:
            body = self.get_unscanned()
        except ScannerEOFError:
            pass
        else:
            yield (None, body)

    def scan_next_stanza(self) -> Iterator[tuple[str, str]]:
        """
        Scan the remaining input for RFC 822-style header fields and return a
        generator of ``(name, value)`` pairs for each header field in the
        input.  Input processing stops as soon as a blank line is encountered.
        (If ``skip_leading_newlines`` is true, the function only stops on a
        blank line after a non-blank line.)

        :raises ScannerError: if the header section is malformed
        :raises ScannerEOFError: if all of the input has already been consumed
        """
        if self._eof:
            raise ScannerEOFError()
        name: str | None = None
        value = ""
        begun = False
        more_left = False
        for line in self._data:
            line = line.rstrip("\r\n")
            if line.startswith((" ", "\t")):
                begun = True
                if name is not None:
                    value += "\n" + line
                else:
                    raise UnexpectedFoldingError(line)
            else:
                m = self.separator_regex.search(line)
                if m:
                    begun = True
                    if name is not None:
                        yield (name, value)
                    name = line[: m.start()]
                    value = line[m.end() :]
                elif line == "":
                    if self.skip_leading_newlines and not begun:
                        continue
                    else:
                        more_left = True
                        break
                else:
                    raise MalformedHeaderError(line)
        if name is not None:
            yield (name, value)
        if not more_left:
            self._eof = True

    def scan_stanzas(self) -> Iterator[list[tuple[str, str]]]:
        """
        Scan the remaining input for zero or more stanzas of RFC 822-style
        header fields and return a generator of lists of ``(name, value)``
        pairs, where each list represents a stanza of header fields in the
        input.

        The stanzas are terminated by blank lines.  Consecutive blank lines
        between stanzas are treated as a single blank line.  Blank lines at the
        end of the input are discarded without creating a new stanza.

        :raises ScannerError: if the header section is malformed
        :raises ScannerEOFError: if all of the input has already been consumed
        """
        if self._eof:
            raise ScannerEOFError()
        while True:
            try:
                fields = list(self.scan_next_stanza())
            except ScannerEOFError:
                break
            if fields or not self._eof:
                yield fields
            else:
                break  # type: ignore[unreachable]
            self.skip_leading_newlines = True

    def get_unscanned(self) -> str:
        """
        Return all of the input that has not yet been processed.  After calling
        this method, calling any method again on the same `Scanner` instance
        will raise `ScannerEOFError`.

        :raises ScannerEOFError: if all of the input has already been consumed
        """
        if self._eof:
            raise ScannerEOFError()
        else:
            return "".join(self._data)


@deprecated(version="0.5.0", reason="use scan() instead")
def scan_string(
    s: str,
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> Iterator[FieldType]:
    """
    Scan a string for RFC 822-style header fields and return a generator of
    ``(name, value)`` pairs for each header field in the input, plus a ``(None,
    body)`` pair representing the body (if any) after the header section.

    See `scan()` for more information on the exact behavior of the scanner.

    .. deprecated:: 0.5.0
        Use `scan()` instead.

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan()`
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return scan(  # pragma: no cover
        s,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    )


def scan(
    data: str | Iterable[str],
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> Iterator[FieldType]:
    """
    .. versionadded:: 0.4.0

    Scan a string, text-file-like object, or iterable of lines for RFC
    822-style header fields and return a generator of ``(name, value)`` pairs
    for each header field in the input, plus a ``(None, body)`` pair
    representing the body (if any) after the header section.

    If ``data`` is a string, it will be broken into lines on CR, LF, and CR LF
    boundaries.

    All lines after the first blank line are concatenated & yielded as-is in a
    ``(None, body)`` pair.  (Note that body lines which do not end with a line
    terminator will not have one appended.)  If there is no empty line in
    ``data``, then no body pair is yielded.  If the empty line is the last line
    in ``data``, the body will be the empty string.  If the empty line is the
    *first* line in ``data`` and the ``skip_leading_newlines`` option is false
    (the default), then all other lines will be treated as part of the body and
    will not be scanned for header fields.

    .. versionchanged:: 0.5.0
        ``data`` can now be a string.

    :param data: a string, text-file-like object, or iterable of strings
        representing lines of input
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return Scanner(
        data,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    ).scan()


@deprecated(version="0.5.0", reason="use Scanner.scan_next_stanza() instead")
def scan_next_stanza(
    iterator: Iterator[str],
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> Iterator[tuple[str, str]]:
    """
    .. versionadded:: 0.4.0

    Scan a text-file-like object or iterator of lines for RFC 822-style header
    fields and return a generator of ``(name, value)`` pairs for each header
    field in the input.  Input processing stops as soon as a blank line is
    encountered, leaving the rest of the iterator unconsumed (If
    ``skip_leading_newlines`` is true, the function only stops on a blank line
    after a non-blank line).

    .. deprecated:: 0.5.0
        Use `Scanner.scan_next_stanza()` instead

    :param iterator: a text-file-like object or iterator of strings
        representing lines of input
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: generator of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return Scanner(
        iterator,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    ).scan_next_stanza()


@deprecated(version="0.5.0", reason="use Scanner.scan_next_stanza() instead")
def scan_next_stanza_string(
    s: str,
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> tuple[list[tuple[str, str]], str]:
    """
    .. versionadded:: 0.4.0

    Scan a string for RFC 822-style header fields and return a pair ``(fields,
    extra)`` where ``fields`` is a list of ``(name, value)`` pairs for each
    header field in the input up to the first blank line and ``extra`` is
    everything after the first blank line (If ``skip_leading_newlines`` is
    true, the dividing point is instead the first blank line after a non-blank
    line); if there is no appropriate blank line in the input, ``extra`` is the
    empty string.

    .. deprecated:: 0.5.0
        Use `Scanner.scan_next_stanza()` instead

    :param s: a string to scan
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: pair of a list of pairs of strings and a string
    :raises ScannerError: if the header section is malformed
    """
    sc = Scanner(
        s,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    )
    fields = list(sc.scan_next_stanza())
    try:
        extra = sc.get_unscanned()
    except ScannerEOFError:
        extra = ""
    return (fields, extra)


def scan_stanzas(
    data: str | Iterable[str],
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> Iterator[list[tuple[str, str]]]:
    """
    .. versionadded:: 0.4.0

    Scan a string, text-file-like object, or iterable of lines for zero or more
    stanzas of RFC 822-style header fields and return a generator of lists of
    ``(name, value)`` pairs, where each list represents a stanza of header
    fields in the input.

    If ``data`` is a string, it will be broken into lines on CR, LF, and CR LF
    boundaries.

    The stanzas are terminated by blank lines.  Consecutive blank lines between
    stanzas are treated as a single blank line.  Blank lines at the end of the
    input are discarded without creating a new stanza.

    .. versionchanged:: 0.5.0
        ``data`` can now be a string.

    :param data: a string, text-file-like object, or iterable of strings
        representing lines of input
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: generator of lists of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return Scanner(
        data,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    ).scan_stanzas()


@deprecated(version="0.5.0", reason="use scan_stanzas() instead")
def scan_stanzas_string(
    s: str,
    *,
    separator_regex: RgxType | None = None,
    skip_leading_newlines: bool = False,
) -> Iterator[list[tuple[str, str]]]:
    """
    .. versionadded:: 0.4.0

    Scan a string for zero or more stanzas of RFC 822-style header fields and
    return a generator of lists of ``(name, value)`` pairs, where each list
    represents a stanza of header fields in the input.

    The stanzas are terminated by blank lines.  Consecutive blank lines between
    stanzas are treated as a single blank line.  Blank lines at the end of the
    input are discarded without creating a new stanza.

    .. deprecated:: 0.5.0
        Use `scan_stanzas()` instead

    :param s: a string which will be broken into lines on CR, LF, and CR LF
        boundaries and passed to `scan_stanzas()`
    :param kwargs: Passed to the `Scanner` constructor
    :rtype: generator of lists of pairs of strings
    :raises ScannerError: if the header section is malformed
    """
    return scan_stanzas(  # pragma: no cover
        s,
        separator_regex=separator_regex,
        skip_leading_newlines=skip_leading_newlines,
    )
