class Error(Exception):
    pass

class ParserError(Error, ValueError):
    pass

class MissingHeaderError(ParserError):
    def __init__(self, header):
        self.header = header

class UnknownHeaderError(ParserError):
    def __init__(self, header):
        self.header = header

class DuplicateHeaderError(ParserError):
    def __init__(self, header):
        self.header = header

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
