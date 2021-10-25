"""
argparse for mail-style headers

``headerparser`` parses key-value pairs in the style of RFC 822 (e-mail)
headers and converts them into case-insensitive dictionaries with the trailing
message body (if any) attached.  Fields can be converted to other types, marked
required, or given default values using an API based on the standard library's
``argparse`` module.  (Everyone loves ``argparse``, right?) Low-level functions
for just scanning header fields (breaking them into sequences of key-value
pairs without any further processing) are also included.

Visit <https://github.com/jwodder/headerparser> or
<http://headerparser.rtfd.io> for more information.
"""

from .errors import (
    BodyNotAllowedError,
    DuplicateBodyError,
    DuplicateFieldError,
    Error,
    FieldTypeError,
    InvalidChoiceError,
    MalformedHeaderError,
    MissingBodyError,
    MissingFieldError,
    ParserError,
    ScannerEOFError,
    ScannerError,
    UnexpectedFoldingError,
    UnknownFieldError,
)
from .normdict import NormalizedDict
from .parscls import (
    BodyField,
    ExtraFields,
    Field,
    MultiExtraFields,
    MultiField,
    parsable,
    parse,
)
from .parser import HeaderParser
from .scanner import (
    Scanner,
    scan,
    scan_next_stanza,
    scan_next_stanza_string,
    scan_stanzas,
    scan_stanzas_string,
    scan_string,
)
from .types import BOOL, decode_bool, decode_value, lower, multidict, unfold

__version__ = "0.5.1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "headerparser@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/headerparser"

__all__ = [
    "BOOL",
    "BodyField",
    "BodyNotAllowedError",
    "DuplicateBodyError",
    "DuplicateFieldError",
    "Error",
    "ExtraFields",
    "Field",
    "FieldTypeError",
    "HeaderParser",
    "InvalidChoiceError",
    "MalformedHeaderError",
    "MissingBodyError",
    "MissingFieldError",
    "MultiExtraFields",
    "MultiField",
    "NormalizedDict",
    "ParserError",
    "Scanner",
    "ScannerEOFError",
    "ScannerError",
    "UnexpectedFoldingError",
    "UnknownFieldError",
    "decode_bool",
    "decode_value",
    "lower",
    "multidict",
    "parsable",
    "parse",
    "scan",
    "scan_next_stanza",
    "scan_next_stanza_string",
    "scan_stanzas",
    "scan_stanzas_string",
    "scan_string",
    "unfold",
]
