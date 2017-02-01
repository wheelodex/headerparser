- Write a README
- Write docstrings
- Set up a Readthedocs site
- Fill in the exception classes
    - Add an exception class for a missing body
    - Add an exception class for an unexpected body
    - Try to include the header name in `HeaderTypeError`s

- Write more tests
    - Test `NormalizedDict`
    - Header definition options:
        - `type`
            - builtin type as `type`
        - `unfold`
        - `dest`
        - multiple names for the same header
            - Defining the same header more than once
        - `required=True` + a header value set (via `type`) to `None`
    - different header name normalizers (identity, hyphens=underscores,
      titlecase?, etc.)
    - `add_additional`
    - `body=False`
    - scanning/parsing multiple stanzas


Features
========
- Add some sort of handling for "From " lines
    - Give `NormalizedDict` a `from_line` attribute
    - Give the scanner a `from_line_regex` parameter; if the first line of a
      stanza matches the regex, it is assumed to be a "From" line, and the
      scanner yields `(line, None)`
    - Give the parser an option for requiring a "From" line
    - Export premade regexes for matching Unix mail "From " lines, HTTP
      request lines, and HTTP response status lines

- Add a scanner function (and parser methods) that takes an iterator of lines
  and only consumes the header lines and the terminating blank line, leaving
  the body in the iterator

- Write an entry point for converting RFC822-style files/headers to JSON
    - name: `mail2json`?
    - include options for:
        - parsing multiple stanzas into an array of JSON objects
        - setting the key name for the "message body"
        - handling of multiple occurrences of the same header in a single
          stanza; choices:
            - only use the first value for each header
            - only use the last value
            - raise an error
            - combine multi-occurrence headers into an array of values
            - use an array of values for all headers regardless of multiplicity
              (default?)
            - output an array of `{"header": ..., "value": ...}` objects
        - handling of non-ASCII characters and the various ways in which they
          can be escaped
        - folding of multiline headers
        - parsing of various structured fields (e.g., Content-Type or To)
        - handling of "From " lines (and/or other non-header headers like the
          first line of an HTTP request or response?)
        - handling of header lettercases?

Scanning
--------
- Add a `bytes` variant of the scanner

- Give the scanner options for:
    - allowed characters in header names (standard: printable ASCII characters
      other than colon and whitespace)
        - whether to allow non-ASCII characters in header names
    - definition of "whitespace" for purposes of unfolding (standard: 0x20 and
      TAB)
    - line separator/terminator (default: CR, LF, and CRLF; standard: only
      CRLF)
        - handling of lone CR and LF when CRLF is used as the line separator
          (standard: obsolete)
    - header name-value delimiter (standard/default: just a colon)
        - Doesn't this make the "allowed characters in header names" option
          unnecessary?
    - stripping whitespace (definable?) after the name-value delimiter?
    - stripping leading whitespace from folded lines? (standard: no)
    - handling "From " lines and the like
    - skipping empty lines at the beginning of the input (instead of treating
      them as ending an empty header stanza)
    - comments? (cf. robots.txt)
    - Error handling:
        - header lines without a colon or indentation (options: error, header
          with empty value, or start of body)
        - empty header name (options: error, header with empty name, look for
          next colon, or start of body)
        - all-whitespace line (considered obsolete by RFC 5322)

Parsing
-------
- Add a separate "`BytesHeaderParser`" class that decodes headers (or just
  names? neither?) and leaves the body as bytes
    - Give its `parse*` methods `encoding` parameters?

- Add built-in support for multi-stanza documents in which different stanzas
  follow different schemata? (e.g., one of the Debian source control file
  formats)

- Include utility callables for header types:
    - RFC822 dates, addresses, etc.
    - Content-Type-style "parameterized" headers
        - Include an `object_pairs_hook` for the parameters?
    - internationalized strings
    - converting lines with just '.' to blank lines
    - Somehow support the types in `email.headerregistry`
    - Provide a `Normalizer` class with options for casing, trimming
      whitespace, squashing whitespace, converting hyphens and underscores to
      the same character, squashing hyphens & underscores, etc.

- Add an option to the parser for requiring that headers occur in the order
  that they are defined?  (The PEP parsing code would appreciate this.)

- Add `object_hook` and `object_pairs_hook` options? (But how would the body be
  handled then?)

- New `add_header` and `add_additional` options to add:
    - `action=callable`
        - The callable should take three arguments: the `NormalizedDict` so
          far, the header name, and the value
    - `mode in ('first', 'last', 'error')` (default: `error`) — defines how to
      handle multiple occurrences of the same header when that header isn't
      `multiple=True`
    - `i18n=bool` — turns on decoding of internationalized mail headers before
      passing to `type` (Do this via a custom type instead?)
    - `rm_comments` — Remove RFC 822 comments from header values?

- Give `add_additional` an option for controlling whether to normalize
  additional header names before adding them to the dict?
