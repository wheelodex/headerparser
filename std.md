<https://tools.ietf.org/html/rfc5322>

§2.1:

    Note: Common parlance and earlier versions of this specification use the
    term "header" to either refer to the entire header section or to refer to
    an individual header field.  To avoid ambiguity, this document does not use
    the terms "header" or "headers" in isolation, but instead always uses
    "header field" to refer to the individual field and "header section" to
    refer to the entire collection.

§2.2:

    Header fields are lines beginning with a field name, followed by a colon
    (":"), followed by a field body, and terminated by CRLF.  A field name MUST
    be composed of printable US-ASCII characters (i.e., characters that have
    values between 33 and 126, inclusive), except colon.  A field body may be
    composed of printable US-ASCII characters as well as the space (SP, ASCII
    value 32) and horizontal tab (HTAB, ASCII value 9) characters (together
    known as the white space characters, WSP).  A field body MUST NOT include
    CR and LF except when used in "folding" and "unfolding", as described in
    section 2.2.3.  All field bodies MUST conform to the syntax described in
    sections 3 and 4 of this specification.
