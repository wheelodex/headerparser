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
    DuplicateFieldError,
    Error,
    FieldTypeError,
    InvalidChoiceError,
    MalformedHeaderError,
    MissingBodyError,
    MissingFieldError,
    ParserError,
    ScannerError,
    UnexpectedFoldingError,
    UnknownFieldError,
)
from .normdict import NormalizedDict
from .parser import HeaderParser
from .scanner import (
    scan,
    scan_next_stanza,
    scan_next_stanza_string,
    scan_stanzas,
    scan_stanzas_string,
    scan_string,
)
from .types import BOOL, lower, unfold

__version__ = "0.5.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "headerparser@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/headerparser"

__all__ = [
    "BOOL",
    "BodyNotAllowedError",
    "DuplicateFieldError",
    "Error",
    "HeaderParser",
    "FieldTypeError",
    "InvalidChoiceError",
    "MalformedHeaderError",
    "MissingBodyError",
    "MissingFieldError",
    "NormalizedDict",
    "ParserError",
    "ScannerError",
    "UnexpectedFoldingError",
    "UnknownFieldError",
    "lower",
    "scan",
    "scan_next_stanza",
    "scan_next_stanza_string",
    "scan_stanzas",
    "scan_stanzas_string",
    "scan_string",
    "unfold",
]
