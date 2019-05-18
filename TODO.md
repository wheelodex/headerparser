- Should string `default` values be passed through `type` etc. like in
  argparse?
- Rethink how the original exception data is attached to `FieldTypeError`s
    - Include everything from `sys.exc_info()`?
- Rename `NormalizedDict.normalized_dict()` to something that doesn't imply it
  returns a `NormalizedDict`?
- Add docstrings to private classes and attributes

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
    - normalizer that returns a non-string
    - non-string keys in `NormalizedDict` with the default normalizer
    - equality of `HeaderParser` objects
    - Test that `HeaderParser.parse_stream()` won't choke on non-string inputs
    - passing scanner options to `HeaderParser`
    - scanning files not opened in universal newlines mode

- Improve documentation & examples
    - Contrast handling of multi-occurrence fields with that of the standard
      library
    - Draw attention to the case-insensitivity of field names when parsing and
      when retriving from the dict
    - Give examples of custom normalization (or at least explain what it is and
      why it's worth having)
    - Add `action` examples


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

- Write an entry point for converting RFC822-style files/headers to JSON
    - name: `mail2json`? `headers2json`?
    - include options for:
        - parsing multiple stanzas into an array of JSON objects
        - setting the key name for the "message body"
        - handling of multiple occurrences of the same header in a single
          stanza; choices:
            - raise an error
            - combine multi-occurrence headers into an array of values
            - use an array of values for all headers regardless of multiplicity
              (default?)
            - output an array of `{"header": ..., "value": ...}` objects
        - handling of non-ASCII characters and the various ways in which they
          can be escaped
        - handling of "From " lines (and/or other non-header headers like the
          first line of an HTTP request or response?)
        - handling of header lettercases?

- Add support for multiple header stanzas in a single document
    - Add a scanner function that parses a multi-stanza document and returns an
      iterable of iterables of key-value pairs
    - Give `HeaderParser` `parse_stanzas` and `parse_stanzas_string` methods
      (Rethink names) that return iterables of `NormalizedDict`s
        - Calling these methods when `body=True` results in an error

Scanning
--------
- Give the scanner options for:
    - definition of "whitespace" for purposes of folding (standard: 0x20 and
      TAB)
    - line separator/terminator (default: CR, LF, and CRLF; standard: only
      CRLF, with lone CR and LF being obsolete)
    - using Unicode definitions of line endings and horizontal whitespace
    - stripping leading whitespace from folded lines? (standard: no)
    - handling "From " lines and the like
    - ignoring all blank lines?
    - comments? (cf. robots.txt)
    - internationalization of header names
    - treating `---` as a blank line?
    - Error handling:
        - header lines without a colon or indentation (options: error, header
          with empty value, or start of body)
        - empty header name (options: error, header with empty name, look for
          next colon, or start of body)
        - all-whitespace line (considered obsolete by RFC 5322)

Parsing
-------
- Add built-in support for multi-stanza documents in which different stanzas
  follow different schemata? (e.g., one of the Debian source control file
  formats)

- Include utility callables for header types:
    - RFC822 dates, addresses, etc.
    - Content-Type-style "parameterized" headers
        - Include an `object_pairs_hook` for the parameters?
        - cf. `cgi.parse_header()`
    - internationalized strings
    - converting lines with just '.' to blank lines
    - Somehow support the types in `email.headerregistry`
    - Provide a `Normalizer` class with options for casing, trimming
      whitespace, squashing whitespace, converting hyphens and underscores to
      the same character, squashing hyphens & underscores, etc.
    - unfolding if & only if the first line of the value contains any
      non-whitespace? (cf. most multiline fields in Debian control files)
    - DKIM headers?
    - removing RFC 822 comments?
    - comma-and-space-separated lists?
        - cf. `urllib.request.parse_http_list()`?

- Add an option to the parser for requiring that headers occur in the order
  that they are defined?  (The PEP parsing code would appreciate this.)

- New `add_field` and `add_additional` options to add:
    - `default_action=callable` for defining what to do when a header is absent
    - `multiple_type` and `multiple_action` — like `type` and `action`, but
      called on a list of all values encountered for a `multiple` field
    - `i18n=bool` — turns on decoding of internationalized mail headers before
      passing to `type` (Do this via a custom type instead?)

- Give `add_additional` an option for controlling whether to normalize
  additional header names before adding them to the dict?

- Requiring/forbidding nonempty/non-whitespace bodies

- Add public methods for removing & inspecting header definitions?

- Support constructing a complete `HeaderParser` in a single expression from a
  `dict` rather than having to make multiple calls to `add_field`
    - Support converting a `HeaderParser` instance to such a `dict`

- Support modifying a `HeaderParser`'s field definitions after they're defined?

- Allow two different named fields to have the same `dest` if they both have
  `multiple=True`? (or both `multiple=False`?)

- Give `add_additional` an argument for putting all additional fields in a
  given subdict (or a presupplied arbitrary mapping object?) so that named
  fields can still use custom dests?

- Give parsers a way to store parsed fields in a presupplied arbitrary mapping
  object (or one created from a `dict_factory`/`dict_cls` callable?) instead of
  creating a new NormalizedDict?

- Give `HeaderParser` an option for storing the body in a given `dict` key

- Create a `BODY` token to use as a `dict` key for storing bodies instead of
  storing them as an attribute?

- Add an option/method for ignoring & discarding any unknown/"additional"
  fields
