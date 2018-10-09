.. currentmodule:: headerparser

Scanner
=======

.. autofunction:: scan_file
.. autofunction:: scan_lines(iterable, **kwargs)
.. autofunction:: scan_string

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
   empty header section and the beginning of the message body.

.. versionadded:: 0.3.0
    ``separator_regex``, ``skip_leading_newlines``
