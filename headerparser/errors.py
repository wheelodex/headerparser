class Error(Exception):
    """ Superclass for all custom exceptions raised by the package """
    pass


class ParserError(Error, ValueError):
    """ Superclass for all custom exceptions related to errors in parsing """
    pass


class MissingFieldError(ParserError):
    """
    Raised when a header field marked as required is not present in the input
    """

    def __init__(self, name):
        #: The name of the missing header field
        self.name = name
        super(MissingFieldError, self).__init__(name)

    def __str__(self):
        return 'Required header field {0.name!r} is not present'.format(self)


class UnknownFieldError(ParserError):
    """
    Raised when an unknown header field is encountered and additional header
    fields are not enabled
    """

    def __init__(self, name):
        #: The name of the unknown header field
        self.name = name
        super(UnknownFieldError, self).__init__(name)

    def __str__(self):
        return 'Unknown header field {0.name!r}'.format(self)


class DuplicateFieldError(ParserError):
    """
    Raised when a header field not marked as multiple occurs two or more times
    in the input
    """

    def __init__(self, name):
        #: The name of the duplicated header field
        self.name = name
        super(DuplicateFieldError, self).__init__(name)

    def __str__(self):
        return 'Header field {0.name!r} occurs more than once'.format(self)


class FieldTypeError(ParserError):
    """ Raised when a ``type`` callable raises an exception """

    def __init__(self, name, value, exc_value):
        #: The name of the header field for which the ``type`` callable was
        #: called
        self.name = name
        #: The value on which the ``type`` callable was called
        self.value = value
        #: The exception raised by the ``type`` callable
        self.exc_value = exc_value
        super(FieldTypeError, self).__init__(name, value, exc_value)

    def __str__(self):
        return 'Error while parsing {0.name!r}: {0.value!r}:'\
               ' {0.exc_value.__class__.__name__}: {0.exc_value}'.format(self)


class InvalidChoiceError(ParserError):
    """
    Raised when a header field is given a value that is not one of its allowed
    choices
    """

    def __init__(self, name, value):
        #: The name of the header field
        self.name = name
        #: The invalid value
        self.value = value
        super(InvalidChoiceError, self).__init__(name, value)

    def __str__(self):
        return '{0.value!r} is not a valid choice for {0.name!r}'.format(self)


class MissingBodyError(ParserError):
    """ Raised when ``body=True`` but there is no message body in the input """

    def __str__(self):
        return 'Message body is required but missing'


class BodyNotAllowedError(ParserError):
    """ Raised when ``body=False`` and the parser encounters a message body """

    def __str__(self):
        return 'Message body is present but not allowed'


class ScannerError(Error, ValueError):
    """ Superclass for all custom exceptions related to errors in scanning """
    pass


class MalformedHeaderError(ScannerError):
    """
    Raised when the scanner encounters an invalid header line, i.e., a line
    without either a colon or leading whitespace
    """

    def __init__(self, line):
        #: The invalid header line
        self.line = line
        super(MalformedHeaderError, self).__init__(line)

    def __str__(self):
        return 'Invalid header line found: {0.line!r}'.format(self)


class UnexpectedFoldingError(ScannerError):
    """
    Raised when the scanner encounters a folded (indented) line that is not
    preceded by a valid header line
    """

    def __init__(self, line):
        #: The line containing the unexpected folding (indentation)
        self.line = line
        super(UnexpectedFoldingError, self).__init__(line)

    def __str__(self):
        return 'Indented line without preceding header line found: {0.line!r}'\
               .format(self)
