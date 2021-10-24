import pytest
import headerparser
from headerparser import HeaderParser


def test_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="notfoo")
    parser.add_field("Bar", dest="notbar")
    parser.add_field("Baz")
    msg = parser.parse("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"notfoo": "red", "notbar": "green", "Baz": "blue"}
    assert msg.body is None


def test_dest_conflict() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="quux")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Bar", dest="QUUX")
    assert "destination defined more than once" in str(excinfo.value)


def test_header_vs_eq_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Bar", dest="Foo")
    assert "destination defined more than once" in str(excinfo.value)


def test_header_vs_like_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Bar", dest="foo")
    assert "destination defined more than once" in str(excinfo.value)


def test_dest_vs_eq_header() -> None:
    parser = HeaderParser()
    parser.add_field("Bar", dest="Foo")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Foo")
    assert "destination defined more than once" in str(excinfo.value)


def test_header_eq_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Foo")
    msg = parser.parse("foo: red")
    assert dict(msg) == {"Foo": "red"}
    assert msg.body is None


def test_header_like_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="FOO")
    msg = parser.parse("foo: red")
    assert dict(msg) == {"FOO": "red"}
    assert msg.body is None


def test_header_missing_default_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="FOO", default=42)
    msg = parser.parse("")
    assert dict(msg) == {"FOO": 42}
    assert msg.body is None


def test_switched_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Bar")
    parser.add_field("Bar", dest="Foo")
    msg = parser.parse("Foo: foo\nBar: bar\n")
    assert dict(msg) == {"Bar": "foo", "Foo": "bar"}
    assert msg.body is None


def test_one_missing_required_switched_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Bar", required=True)
    parser.add_field("Bar", dest="Foo", required=True)
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse("Foo: foo\n")
    assert str(excinfo.value) == "Required header field 'Bar' is not present"
    assert excinfo.value.name == "Bar"


def test_missing_default_switched_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Bar", default=42)
    parser.add_field("Bar", dest="Foo", default="17")
    msg = parser.parse("")
    assert dict(msg) == {"Bar": 42, "Foo": "17"}
    assert msg.body is None


def test_one_missing_default_switched_dest() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Bar", default=42)
    parser.add_field("Bar", dest="Foo", default="17")
    msg = parser.parse("Foo: 42")
    assert dict(msg) == {"Bar": "42", "Foo": "17"}
    assert msg.body is None


def test_dest_multiple() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="list", multiple=True)
    msg = parser.parse("Foo: red\nFoo: green\nFoo: blue")
    assert dict(msg) == {"list": ["red", "green", "blue"]}
    assert msg.body is None


def test_dest_as_unknown_header() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", dest="Bar")
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        parser.parse("Bar: not a header")
    assert str(excinfo.value) == "Unknown header field 'Bar'"
    assert excinfo.value.name == "Bar"
