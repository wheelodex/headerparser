from .errors   import (
                        Error,
                            ParserError,
                                DuplicateFieldError,
                                FieldTypeError,
                                InvalidChoiceError,
                                MissingFieldError,
                                UnknownFieldError,
                                MissingBodyError,
                                BodyNotAllowedError,
                            ScannerError,
                                MalformedHeaderError,
                                UnexpectedFoldingError,
                      )
from .normdict import NormalizedDict
from .parser   import HeaderParser
from .scanner  import scan_file, scan_lines, scan_string
from .types    import BOOL, lower

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'headerparser@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/headerparser'

__all__ = [
    'BOOL',
    'BodyNotAllowedError',
    'DuplicateFieldError',
    'Error',
    'HeaderParser',
    'FieldTypeError',
    'InvalidChoiceError',
    'MalformedHeaderError',
    'MissingBodyError',
    'MissingFieldError',
    'NormalizedDict',
    'ParserError',
    'ScannerError',
    'UnexpectedFoldingError',
    'UnknownFieldError',
    'lower',
    'scan_file',
    'scan_lines',
    'scan_string',
]
