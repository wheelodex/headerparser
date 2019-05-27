.. currentmodule:: headerparser

Scanner
=======

Scanner functions perform basic parsing of RFC 822-style header fields,
splitting them up into sequences of ``(name, value)`` pairs without any further
validation or transformation.

In each pair, the first element (the header field name) is the substring up to
but not including the first whitespace-padded colon (or other delimiter
specified by ``separator_regex``) in the first source line of the header field.
The second element (the header field value) is a single string, the
concatenation of one or more lines, starting with the substring after the first
colon in the first source line, with leading whitespace on lines after the
first preserved; the ending of each line is converted to ``'\n'`` (added if
there is no line ending in the actual input), and the last line of the field
value has its trailing line ending (if any) removed.

.. note::

    "Line ending" here means a CR, LF, or CR LF sequence.  Unicode line
    separators are not treated as line endings and are not trimmed or converted
    to ``'\n'``.

The various functions differ in how they behave once the end of the header
section is encountered:

- `scan()` and `scan_string()` gather up everything after the header section
  and (if there is anything) yield it as a ``(None, body)`` pair

- `scan_next_stanza()` and `scan_next_stanza_string()` stop processing input at
  the end of the header section; `scan_next_stanza()` leaves the unprocessed
  input in the iterator, while `scan_next_stanza_string()` returns the rest of
  the input alongside the header fields

- `scan_stanzas()` and `scan_stanzas_string()` expect their input to consist
  entirely of multiple blank-line-terminated header sections, all of which are
  processed

The `scan()`, `scan_next_stanza()`, and `scan_stanzas()` functions take as
input an iterable of strings (e.g., a text file object) and treat each string
as a single line, regardless of whether it ends with a line ending or not (or
even whether it contains a line ending in the middle of the string).

The `scan_string()`, `scan_next_stanza_string()`, and `scan_stanzas_string()`
functions take as input a single string which is then broken into lines on CR,
LF, and CR LF boundaries and then processed as a list of strings.

.. autofunction:: scan
.. autofunction:: scan_string
.. autofunction:: scan_next_stanza
.. autofunction:: scan_next_stanza_string
.. autofunction:: scan_stanzas
.. autofunction:: scan_stanzas_string

Deprecated Functions
--------------------
.. autofunction:: scan_file
.. autofunction:: scan_lines

.. _scan_opts:

Scanner Options
---------------

The following keyword arguments can be passed to `HeaderParser` and the scanner
functions in order to configure scanning behavior:

``separator_regex=r'[ \t]*:[ \t]*'``
   A regex (as a `str` or compiled regex object) defining the name-value
   separator.  When the regex matches a line, everything before the matched
   substring becomes the field name, and everything after becomes the first
   line of the field value.  Note that the regex must match any surrounding
   whitespace in order for it to be trimmed from the key & value.

``skip_leading_newlines=False``
   If `True`, blank lines at the beginning of the input will be discarded.  If
   `False`, a blank line at the beginning of the input marks the end of an
   empty header section.

.. versionadded:: 0.3.0
    ``separator_regex``, ``skip_leading_newlines``
