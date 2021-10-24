from io import StringIO
import re
from typing import Any, Callable, Iterator, List, cast
from _pytest.fixtures import FixtureRequest
import pytest
import headerparser
from headerparser import scan
from headerparser.scanner import FieldType

ScannerType = Callable[..., Iterator[FieldType]]


def scan_string_as_file(s: str, **kwargs: Any) -> Iterator[FieldType]:
    return scan(StringIO(s), **kwargs)


def scan_string_as_list(s: str, **kwargs: Any) -> Iterator[FieldType]:
    return scan(s.splitlines(True), **kwargs)


def scan_string(s: str, **kwargs: Any) -> Iterator[FieldType]:
    return scan(s, **kwargs)


@pytest.fixture(params=[scan_string_as_file, scan_string_as_list, scan_string])
def scanner(request: FixtureRequest) -> ScannerType:
    return cast(ScannerType, request.param)  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "lines,fields",
    [
        ("", []),
        (
            "Foo: red\nBar: green\nBaz: blue\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        ),
        (
            "Foo: red\nBar: green\nBaz: blue\n\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue"), (None, "")],
        ),
        (
            "Foo: red\nBar: green\nBaz: blue\n\n\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue"), (None, "\n")],
        ),
        (
            "Foo: red\nBar: green\nBaz: blue\n\nThis is a test.",
            [
                ("Foo", "red"),
                ("Bar", "green"),
                ("Baz", "blue"),
                (None, "This is a test."),
            ],
        ),
        (
            "Foo: red\nBar: green\nBaz: blue\n\n\nThis is a test.",
            [
                ("Foo", "red"),
                ("Bar", "green"),
                ("Baz", "blue"),
                (None, "\nThis is a test."),
            ],
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Foo: quux\n"
            "Bar: glarch\n"
            "Baz: cleesh\n",
            [
                ("Foo", "red"),
                ("Bar", "green"),
                ("Baz", "blue"),
                (None, "Foo: quux\nBar: glarch\nBaz: cleesh\n"),
            ],
        ),
        (
            "Key1: Value1\nKey2 :Value2\nKey3 : Value3\nKey4:Value4\n",
            [
                ("Key1", "Value1"),
                ("Key2", "Value2"),
                ("Key3", "Value3"),
                ("Key4", "Value4"),
            ],
        ),
        (
            "Key1: Value1\n"
            "  Folded\n"
            "    More folds\n"
            "Key2: Value2\n"
            "    Folded\n"
            "  Fewer folds\n"
            "Key3: Value3\n"
            "  Key4: Not a real header\n"
            "Key4: \n"
            "\tTab after empty line\n"
            "  \n"
            ' After an "empty" folded line\n'
            "Key5:\n"
            " After a line without even a space!\n",
            [
                ("Key1", "Value1\n  Folded\n    More folds"),
                ("Key2", "Value2\n    Folded\n  Fewer folds"),
                ("Key3", "Value3\n  Key4: Not a real header"),
                ("Key4", '\n\tTab after empty line\n  \n After an "empty" folded line'),
                ("Key5", "\n After a line without even a space!"),
            ],
        ),
        (
            "Foo: red\nBar: green\nBaz: blue",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        ),
        (
            "Foo: red\r\nBar: green\r\nBaz: blue\r\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        ),
        (
            "Foo: value1\nFoo: value2\nFOO: VALUE3\nfOO: valueFour\n",
            [
                ("Foo", "value1"),
                ("Foo", "value2"),
                ("FOO", "VALUE3"),
                ("fOO", "valueFour"),
            ],
        ),
        (
            "Leading:   value\n"
            "Trailing: value  \n"
            "Leading-Tab:\tvalue\n"
            "Trailing-Tab:value\t\n",
            [
                ("Leading", "value"),
                ("Trailing", "value  "),
                ("Leading-Tab", "value"),
                ("Trailing-Tab", "value\t"),
            ],
        ),
        ("Key Name: value", [("Key Name", "value")]),
        ("Foo: red : crimson: scarlet\n", [("Foo", "red : crimson: scarlet")]),
    ],
)
@pytest.mark.parametrize("skip_leading_newlines", [True, False])
def test_scan(
    lines: str,
    fields: List[FieldType],
    skip_leading_newlines: bool,
    scanner: ScannerType,
) -> None:
    assert list(scanner(lines, skip_leading_newlines=skip_leading_newlines)) == fields


@pytest.mark.parametrize(
    "lines,fields,skip_leading_newlines",
    [
        (
            "\nFoo: red\nBar: green\nBaz: blue\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            True,
        ),
        (
            "\nFoo: red\nBar: green\nBaz: blue\n",
            [(None, "Foo: red\nBar: green\nBaz: blue\n")],
            False,
        ),
        ("\n", [(None, "")], False),
        ("\n", [], True),
        ("\n\n", [(None, "\n")], False),
        ("\n\n", [], True),
    ],
)
def test_scan_skip(
    lines: str,
    fields: List[FieldType],
    skip_leading_newlines: bool,
    scanner: ScannerType,
) -> None:
    assert list(scanner(lines, skip_leading_newlines=skip_leading_newlines)) == fields


@pytest.mark.parametrize(
    "lines,fields,separator_regex",
    [
        (
            "Key1: Value1\nKey2 :Value2\nKey3 : Value3\nKey4:Value4\n",
            [
                ("Key1", " Value1"),
                ("Key2 ", "Value2"),
                ("Key3 ", " Value3"),
                ("Key4", "Value4"),
            ],
            ":",
        ),
        (
            "Foo = red\nBar =green\nBaz= blue\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            r"\s*=\s*",
        ),
        (
            "Foo = red\nBar =green\nBaz= blue\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            re.compile(r"\s*=\s*"),
        ),
        (
            "Foo = red = crimson=scarlet\n",
            [("Foo", "red = crimson=scarlet")],
            r"\s*=\s*",
        ),
        (
            "Key: Value = foo\nKey = Value: foo\n",
            [("Key: Value", "foo"), ("Key", "Value: foo")],
            r"\s*=\s*",
        ),
    ],
)
def test_scan_separator_regex(
    lines: str, fields: List[FieldType], separator_regex: bool, scanner: ScannerType
) -> None:
    assert list(scanner(lines, separator_regex=separator_regex)) == fields


@pytest.mark.parametrize(
    "lines,fields",
    [
        (
            "Foo: red\rBar: green\rBaz: blue\r",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        ),
        (
            "Foo: red\nBar: green\rBaz: blue\r\n",
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        ),
        (
            "Foo: line\n"
            "  feed\n"
            "Bar: carriage\r"
            "  return\r"
            "Baz: CR\r\n"
            "  LF\r\n",
            [
                ("Foo", "line\n  feed"),
                ("Bar", "carriage\n  return"),
                ("Baz", "CR\n  LF"),
            ],
        ),
    ],
)
@pytest.mark.parametrize("skip_leading_newlines", [True, False])
def test_scan_string(
    lines: str, fields: List[FieldType], skip_leading_newlines: bool
) -> None:
    assert list(scan(lines, skip_leading_newlines=skip_leading_newlines)) == fields


def test_lines_no_ends() -> None:
    assert list(
        scan(
            [
                "Key: value",
                "Folded: hold on",
                "  let me check",
                " ",
                "  yes",
                "",
                "Newlines will not be added to this body.",
                "So it'll look bad.",
            ]
        )
    ) == [
        ("Key", "value"),
        ("Folded", "hold on\n  let me check\n \n  yes"),
        (None, "Newlines will not be added to this body.So it'll look bad."),
    ]


def test_malformed_header(scanner: ScannerType) -> None:
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scanner("Foo: red\nBar green\nBaz: blue\n"))
    assert str(excinfo.value) == "Invalid header line encountered: 'Bar green'"
    assert excinfo.value.line == "Bar green"


def test_unexpected_folding(scanner: ScannerType) -> None:
    with pytest.raises(headerparser.UnexpectedFoldingError) as excinfo:
        list(scanner(" Foo: red\nBar green\nBaz: blue\n"))
    assert str(excinfo.value) == (
        "Indented line without preceding header line encountered: ' Foo: red'"
    )
    assert excinfo.value.line == " Foo: red"


def test_separator_regex_default_separator(scanner: ScannerType) -> None:
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scanner("Foo = red\nBar: green\n", separator_regex=r"\s*=\s*"))
    assert str(excinfo.value) == "Invalid header line encountered: 'Bar: green'"
    assert excinfo.value.line == "Bar: green"
