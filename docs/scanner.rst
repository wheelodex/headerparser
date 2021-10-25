.. currentmodule:: headerparser

Scanner
=======

The `Scanner` class and related functions perform basic parsing of RFC
822-style header fields, splitting formatted input up into sequences of
``(name, value)`` pairs without any further validation or transformation.

Each pair returned by a scanner method or function represents an individual
header field.  The first element (the header field name) is the substring up to
but not including the first whitespace-padded colon (or other delimiter
specified by ``separator_regex``) in the first source line of the header field.
The second element (the header field value) is a single string, the
concatenation of one or more lines, starting with the substring after the first
colon in the first source line, with leading whitespace on lines after the
first preserved; the ending of each line is converted to ``"\n"`` (added if
there is no line ending in the actual input), and the last line of the field
value has its trailing line ending (if any) removed.

.. note::

    "Line ending" here means a CR, LF, or CR LF sequence.  Unicode line
    separators are not treated as line endings and are not trimmed or converted
    to ``"\n"``.


Scanner Class
-------------
.. autoclass:: Scanner
    :exclude-members: separator_regex, skip_leading_newlines

Functions
---------
.. autofunction:: scan
.. autofunction:: scan_stanzas

Deprecated Functions
--------------------
.. autofunction:: scan_string
.. autofunction:: scan_stanzas_string
.. autofunction:: scan_next_stanza
.. autofunction:: scan_next_stanza_string
