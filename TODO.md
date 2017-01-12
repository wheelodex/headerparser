- Add built-in support for multi-stanza documents in which different stanzas
  follow different schemata? (e.g., one of the Debian source control file
  formats)

- Include utility callables for header types:
    - `BOOL` - supports yes/no, 1/0, and true/false (all case-insensitive)
    - RFC822 dates, addresses, etc.
    - Content-Type-style "parameterized" headers
        - Include an `object_pairs_hook` for the parameters
    - internationalized strings
    - converting lines with just '.' to blank lines

- Somehow support the types in `email.headerregistry`

- Add a `bytes` variant of the lexer
- Add a separate "`RFC822BytesParser`" class that decodes headers (or just
  names? neither?) and leaves the body as bytes
    - Give the `parse*` methods `encoding` parameters?

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

- Add some sort of handling for "From " lines
- Support comments? (cf. robots.txt)

- Give the lexer options for:
   - allowed characters in header names (standard: printable ASCII characters
     other than colon and whitespace)
       - whether to allow non-ASCII characters in header names
   - definition of "whitespace" for purposes of unfolding (standard: 0x20 and
     TAB)
   - line separator/terminator (default: CR, LF, and CRLF; standard: only CRLF)
       - handling of lone CR and LF when CRLF is used as the line separator
         (standard: obsolete)
   - header name-value delimiter (standard/default: just a colon)
       - Doesn't this make the "allowed characters in header names" option
         unnecessary?
   - stripping whitespace (definable?) after the name-value delimiter?
   - stripping leading whitespace from folded lines? (standard: no)
   - handling "From " lines and the like
   - Treating "---" lines as stanza delimiters?
   - Error handling:
       - header lines without a colon or indentation (options: error, header
         with empty value, or start of body)
       - empty header name (options: error, header with empty name, look for
         next colon, or start of body)
       - all-whitespace line (considered obsolete by RFC 5322)

- Add a lexer function (and parser method) that takes an iterator of lines and
  only consumes the header lines and the terminating blank line, leaving the
  body in the iterator
