from typing import List, Tuple
import pytest
from headerparser import Scanner


@pytest.mark.parametrize(
    "lines,fields,trailer,skip_leading_newlines",
    [
        ([], [], "", True),
        ([], [], "", False),
        (["\n", "\n"], [], "", True),
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
            "",
            True,
        ),
        (
            ["Foo: red\n", "Bar: green\n", "Baz: blue\n"],
            [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
            "",
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
def test_scan_next_stanza(
    lines: List[str],
    fields: List[Tuple[str, str]],
    trailer: str,
    skip_leading_newlines: bool,
) -> None:
    sc = Scanner(lines, skip_leading_newlines=skip_leading_newlines)
    assert list(sc.scan_next_stanza()) == fields
    assert sc.get_unscanned() == trailer
    sc = Scanner("".join(lines), skip_leading_newlines=skip_leading_newlines)
    assert list(sc.scan_next_stanza()) == fields
    assert sc.get_unscanned() == trailer
