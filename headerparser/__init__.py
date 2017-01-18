from .normdict import NormalizedDict
from .parser   import HeaderParser
from .scanner  import scan_string

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'headerparser@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/headerparser'

__all__ = [
    'HeaderParser',
    'NormalizedDict',
    'scan_string',
]
