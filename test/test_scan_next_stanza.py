import pytest
from headerparser import scan_next_stanza, scan_next_stanza_string


def test_simple():
    lines = [
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
        "\n",
        "This is a body.\n",
    ]
    liter = iter(lines)
    assert list(scan_next_stanza(liter)) == [
        ("Foo", "red"),
        ("Bar", "green"),
        ("Baz", "blue"),
    ]
    assert list(liter) == ["This is a body.\n"]


def test_simple_string():
    lines = "Foo: red\n" "Bar: green\n" "Baz: blue\n" "\n" "This is a body.\n"
    assert scan_next_stanza_string(lines) == (
        [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        "This is a body.\n",
    )


@pytest.mark.parametrize("skip_leading_newlines", [True, False])
def test_extra_interstitial_blanks(skip_leading_newlines):
    lines = [
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
        "\n",
        "\n",
        "This is a body.\n",
    ]
    liter = iter(lines)
    assert (
        list(
            scan_next_stanza(
                liter,
                skip_leading_newlines=skip_leading_newlines,
            )
        )
        == [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")]
    )
    assert list(liter) == ["\n", "This is a body.\n"]


@pytest.mark.parametrize("skip_leading_newlines", [True, False])
def test_extra_interstitial_blanks_string(skip_leading_newlines):
    lines = "Foo: red\n" "Bar: green\n" "Baz: blue\n" "\n" "\n" "This is a body.\n"
    assert scan_next_stanza_string(
        lines,
        skip_leading_newlines=skip_leading_newlines,
    ) == (
        [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        "\nThis is a body.\n",
    )


def test_leading_blanks_skip():
    lines = [
        "\n",
        "\n",
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
        "\n",
        "This is a body.\n",
    ]
    liter = iter(lines)
    assert list(scan_next_stanza(liter, skip_leading_newlines=True)) == [
        ("Foo", "red"),
        ("Bar", "green"),
        ("Baz", "blue"),
    ]
    assert list(liter) == ["This is a body.\n"]


def test_leading_blanks_skip_string():
    lines = "\n" "\n" "Foo: red\n" "Bar: green\n" "Baz: blue\n" "\n" "This is a body.\n"
    assert scan_next_stanza_string(lines, skip_leading_newlines=True) == (
        [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        "This is a body.\n",
    )


def test_leading_blanks_no_skip():
    lines = [
        "\n",
        "\n",
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
        "\n",
        "This is a body.\n",
    ]
    liter = iter(lines)
    assert list(scan_next_stanza(liter, skip_leading_newlines=False)) == []
    assert list(liter) == [
        "\n",
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
        "\n",
        "This is a body.\n",
    ]


def test_leading_blanks_no_skip_string():
    lines = "\n" "\n" "Foo: red\n" "Bar: green\n" "Baz: blue\n" "\n" "This is a body.\n"
    assert scan_next_stanza_string(lines, skip_leading_newlines=False) == (
        [],
        "\n" "Foo: red\n" "Bar: green\n" "Baz: blue\n" "\n" "This is a body.\n",
    )


def test_stanza_only():
    lines = [
        "Foo: red\n",
        "Bar: green\n",
        "Baz: blue\n",
    ]
    liter = iter(lines)
    assert list(scan_next_stanza(liter)) == [
        ("Foo", "red"),
        ("Bar", "green"),
        ("Baz", "blue"),
    ]
    assert list(liter) == []


def test_stanza_only_string():
    lines = "Foo: red\n" "Bar: green\n" "Baz: blue\n"
    assert scan_next_stanza_string(lines) == (
        [("Foo", "red"), ("Bar", "green"), ("Baz", "blue")],
        "",
    )


def test_empty():
    lines = []
    liter = iter(lines)
    assert list(scan_next_stanza(liter)) == []
    assert list(liter) == []


def test_empty_string():
    assert scan_next_stanza_string("") == ([], "")


def test_all_blanks_skip():
    lines = ["\n", "\n"]
    liter = iter(lines)
    assert list(scan_next_stanza(liter, skip_leading_newlines=True)) == []
    assert list(liter) == []


def test_all_blanks_no_skip():
    lines = ["\n", "\n"]
    liter = iter(lines)
    assert list(scan_next_stanza(liter, skip_leading_newlines=False)) == []
    assert list(liter) == ["\n"]


def test_all_blanks_skip_string():
    assert scan_next_stanza_string("\n\n", skip_leading_newlines=True) == ([], "")


def test_all_blanks_no_skip_string():
    assert scan_next_stanza_string("\n\n", skip_leading_newlines=False) == ([], "\n")
