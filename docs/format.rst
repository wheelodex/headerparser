Input Format
============
`headerparser` accepts a syntax that is intended to be a simplified superset of
the Internet Message (e-mail) Format specified in :rfc:`822`, :rfc:`2822`, and
:rfc:`5322`.  Specifically:

- Everything in the input up to (but not including) the first blank line (i.e.,
  a line containing only a line ending) constitutes the :dfn:`header section`.
  Everything after the first blank line is a free-form :dfn:`message body`.  If
  there are no blank lines, the entire input is used as the header section, and
  there is no body.

- The header section is composed of zero or more :dfn:`header fields`.  A
  header field is composed of one or more lines, with all lines other than the
  first beginning with a space or tab.  Additionally, the first line must
  contain a colon (optionally surrounded by whitespace); everything before the
  colon is the :dfn:`header field name`, while everything after (including
  subsequent lines) is the :dfn:`header field value`.

.. note::

    This format only recognizes CR, LF, and CR LF sequences as line endings.
