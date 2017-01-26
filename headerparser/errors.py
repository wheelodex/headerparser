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

class HeaderTypeError(ParserError):
    def __init__(self, typename, value):
        self.typename = typename
        self.value = value

class InvalidChoiceError(ParserError):
    def __init__(self, header, value):
        self.header = header
        self.value = value

class ScannerError(Error, ValueError):
    pass

class MalformedHeaderError(ScannerError):
    pass

class UnexpectedFoldingError(ScannerError):
    pass

class RedefinitionError(Error, ValueError):
    def __init__(self, header=None, dest=None):
        self.header = header
        self.dest = dest
