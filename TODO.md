- Write docstrings
- Set up a Readthedocs site
    - Include README examples in docs
    - Add a page documenting the exact RFC 822 format recognized, combining the
      documentation from the README and from the `scan_lines` docstring
- Should string `default` values be passed through `type` etc. like in
  argparse?
- Rethink how the original exception data is attached to `FieldTypeError`s
- Give `HeaderParser` an `__eq__` method
- Make `HeaderParser`'s attributes private?

- Write more tests
    - different header name normalizers (identity, hyphens=underscores,
      titlecase?, etc.)
    - `add_additional`
        - calling `add_additional` multiple times (some times with
          `allow=False`)
        - `add_additional(False, extra arguments ...)`
        - `add_additional` when a header has a `dest` that's just a normalized
          form of one of its names
    - calling `add_field`/`add_additional` on a `HeaderParser` after a previous
      call raised an error
    - scanning & parsing Unicode


Features
========
- Add some sort of handling for "From " lines
    - Give `NormalizedDict` a `from_line` attribute
    - Give the scanner a `from_line_regex` parameter; if the first line of a
      stanza matches the regex, it is assumed to be a "From" line
    - Create a "`SpecialHeader`" enum with `FromLine` and `Body` values for use
      as the first element of `(header, value)` pairs yielded by the scanner
      representing "From " lines and bodies
        - Use the enum values as keys in `NormalizedDict`s instead of having
          dedicated `from_line` and `body` attributes?
    - Give the parser an option for requiring a "From " line
    - Export premade regexes for matching Unix mail "From " lines, HTTP
      request lines, and HTTP response status lines

- Add a scanner function (and parser methods) that takes an iterator of lines
  and only consumes the header lines and the terminating blank line, leaving
  the body in the iterator

- Support binary input
    - Add a `bytes` variant of the scanner
    - Add a separate "`BytesHeaderParser`" class that decodes headers (or just
      names? neither?) and leaves the body as bytes
        - Give its `parse*` methods `encoding` parameters?

- Write an entry point for converting RFC822-style files/headers to JSON
    - name: `mail2json`? `headers2json`?
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

- Allow lines passed to `scan_lines` and `parse_lines` to lack terminating
  newlines

- Add support for multiple header stanzas in a single document
    - Add a scanner function that parses a multi-stanza document and returns an
      iterable of iterables of key-value pairs
    - Give `HeaderParser` `parse_stanzas_file` and `parse_stanzas_string`
      methods (Rethink names) that return iterables of `NormalizedDict`s
        - Calling these methods when `body=True` results in an error

Scanning
--------
- Give the scanner options for:
    - header name-value delimiter (standard/default: just a colon)
    - definition of "whitespace" for purposes of folding (standard: 0x20 and
      TAB)
    - line separator/terminator (default: CR, LF, and CRLF; standard: only
      CRLF, with lone CR and LF being obsolete)
    - stripping leading whitespace from folded lines? (standard: no)
    - handling "From " lines and the like
    - skipping empty lines at the beginning of the input (instead of treating
      them as ending an empty header stanza)
    - ignoring all blank lines?
    - comments? (cf. robots.txt)
    - internationalization of header names?
    - Error handling:
        - header lines without a colon or indentation (options: error, header
          with empty value, or start of body)
        - empty header name (options: error, header with empty name, look for
          next colon, or start of body)
        - all-whitespace line (considered obsolete by RFC 5322)

Parsing
-------
- The `HeaderParser` constructor should accept arbitrary `**kwargs` that are
  then passed to the scanner function(s)

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
    - unfolding if & only if the first line of the value contains any
      non-whitespace? (cf. most multiline fields in Debian control files)
    - DKIM headers?

- Add an option to the parser for requiring that headers occur in the order
  that they are defined?  (The PEP parsing code would appreciate this.)

- Add `object_hook` and `object_pairs_hook` options? (But how would the body be
  handled then?)

- New `add_field` and `add_additional` options to add:
    - `action=callable`
        - The callable should take three arguments: the `NormalizedDict` so
          far, the header name, and the value
        - When `action` is defined, `dest` and `multiple` (and `default`?)
          cannot be
    - `i18n=bool` — turns on decoding of internationalized mail headers before
      passing to `type` (Do this via a custom type instead?)
    - `rm_comments` — Remove RFC 822 comments from header values?

- Give `add_additional` an option for controlling whether to normalize
  additional header names before adding them to the dict?

- Requiring/forbidding nonempty/non-whitespace bodies

- Add public methods for removing & inspecting header definitions?
