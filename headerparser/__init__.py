from .errors   import (
                        Error,
                            ParserError,
                                MissingHeaderError,
                                UnknownHeaderError,
                                DuplicateHeaderError,
                            ScannerError,
                                MalformedHeaderError,
                                UnexpectedFoldingError,
                      )
from .normdict import NormalizedDict
from .parser   import HeaderParser
from .scanner  import scan_file, scan_string

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'headerparser@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/headerparser'

__all__ = [
    'DuplicateHeaderError',
    'Error',
    'HeaderParser',
    'MalformedHeaderError',
    'MissingHeaderError',
    'NormalizedDict',
    'ParserError',
    'ScannerError',
    'UnexpectedFoldingError',
    'UnknownHeaderError',
    'scan_file',
    'scan_string',
]
