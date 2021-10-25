from typing import Any


class Error(Exception):
    """Superclass for all custom exceptions raised by the package"""

    pass


class ParserError(Error, ValueError):
    """Superclass for all custom exceptions related to errors in parsing"""

    pass


class MissingFieldError(ParserError):
    """
    Raised when a header field marked as required is not present in the input
    """

    def __init__(self, name: str) -> None:
        #: The name of the missing header field
        self.name: str = name

    def __str__(self) -> str:
        return f"Required header field {self.name!r} is not present"


class UnknownFieldError(ParserError):
    """
    Raised when an unknown header field is encountered and additional header
    fields are not enabled
    """

    def __init__(self, name: str) -> None:
        #: The name of the unknown header field
        self.name: str = name

    def __str__(self) -> str:
        return f"Unknown header field {self.name!r}"


class DuplicateFieldError(ParserError):
    """
    Raised when a header field not marked as multiple occurs two or more times
    in the input
    """

    def __init__(self, name: str) -> None:
        #: The name of the duplicated header field
        self.name: str = name

    def __str__(self) -> str:
        return f"Header field {self.name!r} occurs more than once"


class DuplicateBodyError(ParserError):
    """Raised when a body field occurs two or more times in the input"""

    def __str__(self) -> str:
        return "Body field occurs more than once"


class FieldTypeError(ParserError):
    """Raised when a ``type`` callable raises an exception"""

    def __init__(self, name: str, value: str, exc_value: BaseException) -> None:
        #: The name of the header field for which the ``type`` callable was
        #: called
        self.name: str = name
        #: The value on which the ``type`` callable was called
        self.value: str = value
        #: The exception raised by the ``type`` callable
        self.exc_value: BaseException = exc_value

    def __str__(self) -> str:
        return (
            f"Error while parsing {self.name!r}: {self.value!r}:"
            f" {self.exc_value.__class__.__name__}: {self.exc_value}"
        )


class InvalidChoiceError(ParserError):
    """
    Raised when a header field is given a value that is not one of its allowed
    choices
    """

    def __init__(self, name: str, value: Any) -> None:
        #: The name of the header field
        self.name: str = name
        #: The invalid value
        self.value: Any = value

    def __str__(self) -> str:
        return f"{self.value!r} is not a valid choice for {self.name!r}"


class MissingBodyError(ParserError):
    """Raised when ``body=True`` but there is no message body in the input"""

    def __str__(self) -> str:
        return "Message body is required but missing"


class BodyNotAllowedError(ParserError):
    """Raised when ``body=False`` and the parser encounters a message body"""

    def __str__(self) -> str:
        return "Message body is present but not allowed"


class ScannerError(Error, ValueError):
    """Superclass for all custom exceptions related to errors in scanning"""

    pass


class MalformedHeaderError(ScannerError):
    """
    Raised when the scanner encounters an invalid header line, i.e., a line
    without either a colon or leading whitespace
    """

    def __init__(self, line: str) -> None:
        #: The invalid header line
        self.line: str = line

    def __str__(self) -> str:
        return f"Invalid header line encountered: {self.line!r}"


class UnexpectedFoldingError(ScannerError):
    """
    Raised when the scanner encounters a folded (indented) line that is not
    preceded by a valid header line
    """

    def __init__(self, line: str) -> None:
        #: The line containing the unexpected folding (indentation)
        self.line: str = line

    def __str__(self) -> str:
        return f"Indented line without preceding header line encountered: {self.line!r}"


class ScannerEOFError(Error):
    """
    Raised when a `Scanner` method is called after all input has been exhausted
    """

    def __str__(self) -> str:
        return "Scanner has reached end of input"
