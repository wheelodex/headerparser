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

``skip_leading_newlines=False``
   If `True`, blank lines at the beginning of the input will be discarded.

.. versionadded:: 0.3.0
    ``skip_leading_newlines``
