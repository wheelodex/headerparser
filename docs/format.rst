Input Format
============
`headerparser` accepts a syntax that is intended to be a simplified superset of
the Internet Message (e-mail) Format specified in :rfc:`822`, :rfc:`2822`, and
:rfc:`5322`.  Specifically:

- Everything in the input up to (but not including) the first blank line (i.e.,
  a line containing only a line ending) constitutes a :dfn:`stanza` or
  :dfn:`header section`.  Everything after the first blank line is a free-form
  :dfn:`message body`.  If there are no blank lines, the entire input is used
  as the header section, and there is no body.

.. note::

    By default, blank lines at the beginning of a document are interpreted as
    the ending of a zero-length stanza.  Such blank lines can instead be
    ignored by setting the ``skip_leading_newlines`` :ref:`scanner option
    <scan_opts>` to true.

- A stanza or header section is composed of zero or more :dfn:`header fields`.
  A header field is composed of one or more lines, with all lines after the
  first beginning with a space or tab.  Additionally, the first line must
  contain a colon (optionally surrounded by whitespace); everything before the
  colon is the :dfn:`header field name`, while everything after (including
  subsequent lines) is the :dfn:`header field value`.

.. note::

    Name-value separators other than a colon can be used by setting the
    ``separator_regex`` :ref:`scanner option <scan_opts>` appropriately.

.. note::

    This format only recognizes CR, LF, and CR LF sequences as line endings.

An example::

    Key: Value
    Foo: Bar
    Bar:Whitespace around the colon is optional
    Baz  :  Very optional
    Long-Field: This field has a very long value, so I'm going to split it
      across multiple lines.
      
      The above line is all whitespace.  This counts as line folding, and so
      we're still in the "Long Field" value, but the RFCs consider such lines
      obsolete, so you should avoid using them.
      .
      One alternative to an all-whitespace line is a line with just indentation
      and a period.  Debian package description fields use this.
    Foo: Wait, I already defined a value for this key.  What happens now?
    What happens now: It depends on whether the `multiple` option for the "Foo"
      field was set in the HeaderParser.
    If multiple=True: The "Foo" key in the dictionary returned by
      HeaderParser.parse_string() would map to a list of all of Foo's values
    If multiple=False: A ParserError is raised
    If multiple=False but there's only one "Foo" anyway:
      The "Foo" key in the result dictionary would map to just a single string.
    Compare this to: the standard library's `email` package, which accepts
      multi-occurrence fields, but *which* occurrence Message.__getitem__
      returns is unspecified!

    Are we still in the header: no
      There was a blank line above, so we're now in the body, which isn't
      processed for headers.
    Good thing, too, because this isn't a valid header line.

On the other hand, this is not a valid RFC 822-style document::

        An indented first line — without a "Name:" line before it!
    A header line without a colon isn't good, either.
    Does this make up for the above: no
