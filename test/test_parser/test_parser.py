from typing import Any
import pytest
from pytest_mock import MockerFixture
import headerparser
from headerparser import HeaderParser


def test_simple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_out_of_order() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBaz: blue\nBar: green\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_different_cases() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBAR: green\nbaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_empty_body() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body == ""


def test_blank_body() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n\n\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body == "\n"


def test_body() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n\nThis is a test.")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body == "This is a test."


def test_headerlike_body() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string(
        "Foo: red\n"
        "Bar: green\n"
        "Baz: blue\n"
        "\n"
        "Foo: quux\n"
        "Bar: glarch\n"
        "Baz: cleesh\n"
    )
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body == "Foo: quux\nBar: glarch\nBaz: cleesh\n"


def test_missing() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green"}
    assert msg.body is None


def test_required() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz", required=True)
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_required_default() -> None:
    parser = HeaderParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Foo", required=True, default="Why?")
    assert "required and default are mutually exclusive" in str(excinfo.value)


def test_required_none() -> None:
    parser = HeaderParser()
    parser.add_field("None", required=True, type=lambda _: None)
    msg = parser.parse_string("None: whatever")
    assert dict(msg) == {"None": None}
    assert msg.body is None


def test_missing_required() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz", required=True)
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\n")
    assert str(excinfo.value) == "Required header field 'Baz' is not present"
    assert excinfo.value.name == "Baz"


def test_present_default() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz", default=42)
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_missing_default() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz", default=42)
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": 42}
    assert msg.body is None


def test_missing_None_default() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz", default=None)
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": None}
    assert msg.body is None


def test_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nFOO: magenta\nBar: green\nfoo : crimson\n")
    assert dict(msg) == {"Foo": ["red", "magenta", "crimson"], "Bar": "green"}
    assert msg.body is None


def test_one_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": ["red"], "Bar": "green"}
    assert msg.body is None


def test_no_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True)
    parser.add_field("Bar")
    msg = parser.parse_string("Bar: green\n")
    assert dict(msg) == {"Bar": "green"}
    assert msg.body is None


def test_bad_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True)
    parser.add_field("Bar")
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string("Foo: red\nFOO: magenta\nBar: green\nBar: lime\n")
    assert str(excinfo.value) == "Header field 'Bar' occurs more than once"
    assert excinfo.value.name == "Bar"


def test_default_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, default=42)
    parser.add_field("Bar")
    msg = parser.parse_string("Bar: green\n")
    assert dict(msg) == {"Foo": 42, "Bar": "green"}
    assert msg.body is None


def test_present_default_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, default=42)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": ["red"], "Bar": "green"}
    assert msg.body is None


def test_present_default_many_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, default=42)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nFOO: magenta\nBar: green\n")
    assert dict(msg) == {"Foo": ["red", "magenta"], "Bar": "green"}
    assert msg.body is None


def test_required_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, required=True)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": ["red"], "Bar": "green"}
    assert msg.body is None


def test_required_many_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, required=True)
    parser.add_field("Bar")
    msg = parser.parse_string("Foo: red\nFOO: magenta\nBar: green\n")
    assert dict(msg) == {"Foo": ["red", "magenta"], "Bar": "green"}
    assert msg.body is None


def test_missing_required_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True, required=True)
    parser.add_field("Bar")
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string("Bar: green\n")
    assert str(excinfo.value) == "Required header field 'Foo' is not present"
    assert excinfo.value.name == "Foo"


def test_unknown() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\nQuux: blue\n")
    assert str(excinfo.value) == "Unknown header field 'Quux'"
    assert excinfo.value.name == "Quux"


def test_empty_input() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("")
    assert dict(msg) == {}
    assert msg.body is None


def test_trailing_whitespace() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("Foo: red  \nBar: green\n (ish) \nBaz: blue\n   ")
    assert dict(msg) == {
        "Foo": "red  ",
        "Bar": "green\n (ish) ",
        "Baz": "blue\n   ",
    }
    assert msg.body is None


def test_redefinition() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("FOO")
    assert "field defined more than once" in str(excinfo.value)


def test_many_missing_required() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", required=True)
    parser.add_field("Bar", required=True)
    parser.add_field("Baz", required=True)
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string("")
    assert excinfo.value.name in ("Foo", "Bar", "Baz")


def test_unfold() -> None:
    parser = HeaderParser()
    parser.add_field("Folded")
    parser.add_field("Unfolded", unfold=True)
    msg = parser.parse_string(
        "Folded: This is\n"
        "   test\n"
        "\ttext.\n"
        "UnFolded: This is\n"
        "   test\n"
        "\ttext.\n"
    )
    assert dict(msg) == {
        "Folded": "This is\n   test\n\ttext.",
        "Unfolded": "This is test text.",
    }
    assert msg.body is None


def test_space_in_name() -> None:
    parser = HeaderParser()
    parser.add_field("Key Name")
    parser.add_field("Bar")
    parser.add_field("Baz")
    msg = parser.parse_string("key name: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Key Name": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_scan_opts_passed(mocker: MockerFixture) -> None:
    m = mocker.patch("headerparser.scanner.scan", wraps=headerparser.scanner.scan)
    parser = HeaderParser(
        separator_regex=r"\s*:\s*",
        skip_leading_newlines=True,
    )
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    m.assert_called_with(
        "Foo: red\nBar: green\nBaz: blue\n",
        separator_regex=r"\s*:\s*",
        skip_leading_newlines=True,
    )


def test_body_twice() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_field("Baz")
    with pytest.raises(ValueError) as excinfo:
        parser.parse_stream(
            [
                ("Foo", "red"),
                ("Bar", "green"),
                ("Baz", "blue"),
                (None, "Body #1"),
                (None, "Body #2"),
            ]
        )
    assert str(excinfo.value) == "Body appears twice in input"


@pytest.mark.parametrize("name", [42, None, 3.14, True, ["B", "a", "r"]])
def test_nonstr_field_name(name: Any) -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    with pytest.raises(TypeError) as excinfo:
        parser.add_field(name)
    assert str(excinfo.value) == "field names must be strings"
