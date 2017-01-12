Add options for:

- allowed characters in header names (standard: printable ASCII characters
  other than colon and whitespace)
    - whether to allow non-ASCII characters in header names
- definition of "whitespace" for purposes of unfolding (standard: 0x20 and TAB)
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
    - header lines without a colon or indentation (options: error, header with
      empty value, or start of body)
    - empty header name (options: error, header with empty name, look for next
      colon, or start of body)
    - all-whitespace line (considered obsolete by RFC 5322)
