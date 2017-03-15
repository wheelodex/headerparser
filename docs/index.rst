.. module:: headerparser

==============================================
headerparser — argparse for mail-style headers
==============================================

`headerparser` parses key-value pairs in the style of :rfc:`822` (e-mail)
headers and converts them into case-insensitive dictionaries with the trailing
message body (if any) attached.  Fields can be converted to other types, marked
required, or given default values using an API based on the standard library's
`argparse` module.  (Everyone loves `argparse`, right?) Low-level functions
for just scanning header fields (breaking them into sequences of key-value
pairs without any further processing) are also included.

.. toctree::
    :maxdepth: 2

    format
    parser
    scanner
    errors
    util

Indices and tables
==================
* :ref:`genindex`
* :ref:`search`
