class Error(Exception):
    pass


class ParserError(Error, ValueError):
    pass


class MissingHeaderError(ParserError):
    def __init__(self, header):
        self.header = header
        super(MissingHeaderError, self).__init__(header)

    def __str__(self):
        return 'Required header {0.header!r} is not present'.format(self)


class UnknownHeaderError(ParserError):
    def __init__(self, header):
        self.header = header
        super(UnknownHeaderError, self).__init__(header)

    def __str__(self):
        return 'Unknown header {0.header!r}'.format(self)


class DuplicateHeaderError(ParserError):
    def __init__(self, header):
        self.header = header
        super(DuplicateHeaderError, self).__init__(header)

    def __str__(self):
        return 'Header {0.header!r} occurs more than once'.format(self)


class HeaderTypeError(ParserError):
    def __init__(self, header, value, exc_value):
        self.header = header
        self.value = value
        self.exc_value = exc_value
        super(HeaderTypeError, self).__init__(header, value, exc_value)

    def __str__(self):
        return 'Error while parsing {0.header!r}: {0.value!r}:'\
               ' {0.exc_value.__class__.__name__}: {0.exc_value}'.format(self)


class InvalidChoiceError(ParserError):
    def __init__(self, header, value):
        self.header = header
        self.value = value
        super(InvalidChoiceError, self).__init__(header, value)

    def __str__(self):
        return '{0.value!r} is not a valid choice for {0.header!r}'.format(self)


class MissingBodyError(ParserError):
    def __str__(self):
        return 'Message body is required but missing'


class BodyNotAllowedError(ParserError):
    def __str__(self):
        return 'Message body is present but not allowed'


class ScannerError(Error, ValueError):
    pass


class MalformedHeaderError(ScannerError):
    def __init__(self, line):
        self.line = line
        super(MalformedHeaderError, self).__init__(line)

    def __str__(self):
        return 'Invalid header line found: {0.line!r}'.format(self)


class UnexpectedFoldingError(ScannerError):
    def __init__(self, line):
        self.line = line
        super(UnexpectedFoldingError, self).__init__(line)

    def __str__(self):
        return 'Indented line without preceding header line found: {0.line!r}'\
               .format(self)
