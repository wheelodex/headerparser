from io import StringIO
from typing import Callable, Iterator, List, Tuple
import pytest
from headerparser import MalformedHeaderError, scan_stanzas, scan_stanzas_string

ScannerType = Callable[[str, bool], Iterator[List[Tuple[str, str]]]]


def scan_stanzas_string_as_file(
    s: str, skip_leading_newlines: bool = False
) -> Iterator[List[Tuple[str, str]]]:
    return scan_stanzas(StringIO(s), skip_leading_newlines=skip_leading_newlines)


def scan_stanzas_string_as_list(s: str, skip_leading_newlines: bool = False):
    return scan_stanzas(s.splitlines(True), skip_leading_newlines=skip_leading_newlines)


@pytest.fixture(
    params=[
        scan_stanzas_string_as_file,
        scan_stanzas_string_as_list,
        scan_stanzas_string,
    ]
)
def scanner(request) -> ScannerType:
    return request.param


@pytest.mark.parametrize(
    "lines,fields,skip_leading_newlines",
    [
        ("", [], True),
        ("", [], False),
        ("\n\n", [], True),
        ("\n\n", [[]], False),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            True,
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            False,
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            True,
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            False,
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n"
            "\n"
            "\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            True,
        ),
        (
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n"
            "\n"
            "\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            False,
        ),
        (
            "\n"
            "\n"
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            True,
        ),
        (
            "\n"
            "\n"
            "Foo: red\n"
            "Bar: green\n"
            "Baz: blue\n"
            "\n"
            "Quux: ruby\n"
            "Glarch: sapphire\n"
            "Cleesh: garnet\n"
            "\n"
            "Blue: foo\n"
            "Red: bar\n"
            "Green: baz\n",
            [
                [],
                [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
                [("Quux", "ruby"), ("Glarch", "sapphire"), ("Cleesh", "garnet")],
                [("Blue", "foo"), ("Red", "bar"), ("Green", "baz")],
            ],
            False,
        ),
    ],
)
def test_scan_stanzas(
    lines: str,
    fields: List[List[Tuple[str, str]]],
    skip_leading_newlines: bool,
    scanner: ScannerType,
) -> None:
    assert list(scanner(lines, skip_leading_newlines=skip_leading_newlines)) == fields


def test_invalid_stanza(scanner: ScannerType) -> None:
    stanzas = scanner(
        "Foo: red\n"
        "Bar: green\n"
        "Baz: blue\n"
        "\n"
        "Quux: ruby\n"
        "Glarch: sapphire\n"
        "Cleesh: garnet\n"
        "\n"
        "Blue: foo\n"
        "Wait, this isn't a header.\n"
        "Green: baz\n",
        skip_leading_newlines=True,
    )
    assert next(stanzas) == [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")]
    assert next(stanzas) == [
        ("Quux", "ruby"),
        ("Glarch", "sapphire"),
        ("Cleesh", "garnet"),
    ]
    with pytest.raises(MalformedHeaderError) as excinfo:
        next(stanzas)
    assert str(excinfo.value) == (
        'Invalid header line encountered: "Wait, this isn\'t a header."'
    )
