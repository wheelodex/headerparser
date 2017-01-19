class Error(Exception):
    pass

class ParserError(Error, ValueError):
    pass

class MissingHeaderError(ParserError):
    pass

class UnknownHeaderError(ParserError):
    pass

class DuplicateHeaderError(ParserError):
    pass

### Add a class for failed "choices" constraints
### Add a class for a missing body
### Add a class for an unexpected body
### Add a class for "type" failures?

class ScannerError(Error, ValueError):
    pass

class MalformedHeaderError(ScannerError):
    pass

class UnexpectedFoldingError(ScannerError):
    pass
