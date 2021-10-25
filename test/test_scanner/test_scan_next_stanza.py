from typing import List, Optional, Tuple
import pytest
from headerparser import (
    Scanner,
    ScannerEOFError,
    scan_next_stanza,
    scan_next_stanza_string,
)


@pytest.mark.parametrize(
    "lines,fields,trailer,skip_leading_newlines",
    [
        ([], [], None, True),
        ([], [], None, False),
        (["\n", "\n"], [], None, True),
        (["\n", "\n"], [], "\n", False),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "This is a body.\n",
            True,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "This is a body.\n",
            False,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "\nThis is a body.\n",
            True,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "\nThis is a body.\n",
            False,
        ),
        (
            ["Foo: red\n", "Bar: green\n", "Baz: blue\n"],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            None,
            True,
        ),
        (
            ["Foo: red\n", "Bar: green\n", "Baz: blue\n"],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            None,
            False,
        ),
        (
            [
                "\n",
                "\n",
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "This is a body.\n",
            True,
        ),
        (
            [
                "\n",
                "\n",
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [],
            "\nFoo: red\nBar: green\nBaz: blue\n\nThis is a body.\n",
            False,
        ),
    ],
)
def test_scanner_next_stanza(
    lines: List[str],
    fields: List[Tuple[str, str]],
    trailer: Optional[str],
    skip_leading_newlines: bool,
) -> None:
    for data in (lines, "".join(lines)):
        sc = Scanner(data, skip_leading_newlines=skip_leading_newlines)
        assert list(sc.scan_next_stanza()) == fields
        try:
            remainder = sc.get_unscanned()
        except ScannerEOFError:
            assert trailer is None
        else:
            assert remainder == trailer


@pytest.mark.filterwarnings("ignore:.*scan_next_stanza")
@pytest.mark.parametrize(
    "lines,fields,trailer,skip_leading_newlines",
    [
        ([], [], [], True),
        ([], [], [], False),
        (["\n", "\n"], [], [], True),
        (["\n", "\n"], [], ["\n"], False),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            ["This is a body.\n"],
            True,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            ["This is a body.\n"],
            False,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            ["\n", "This is a body.\n"],
            True,
        ),
        (
            [
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            ["\n", "This is a body.\n"],
            False,
        ),
        (
            ["Foo: red\n", "Bar: green\n", "Baz: blue\n"],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            [],
            True,
        ),
        (
            ["Foo: red\n", "Bar: green\n", "Baz: blue\n"],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            [],
            False,
        ),
        (
            [
                "\n",
                "\n",
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            ["This is a body.\n"],
            True,
        ),
        (
            [
                "\n",
                "\n",
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            [],
            [
                "\n",
                "Foo: red\n",
                "Bar: green\n",
                "Baz: blue\n",
                "\n",
                "This is a body.\n",
            ],
            False,
        ),
    ],
)
def test_scan_next_stanza(
    lines: List[str],
    fields: List[Tuple[str, str]],
    trailer: List[str],
    skip_leading_newlines: bool,
) -> None:
    liter = iter(lines)
    assert (
        list(scan_next_stanza(liter, skip_leading_newlines=skip_leading_newlines))
        == fields
    )
    assert list(liter) == trailer
    assert scan_next_stanza_string(
        "".join(lines), skip_leading_newlines=skip_leading_newlines
    ) == (fields, "".join(trailer))
