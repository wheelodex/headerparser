from typing import Any
import pytest
from headerparser import BOOL, FieldTypeError, HeaderParser


def test_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL)
    msg = parser.parse("Boolean: yes\n")
    assert dict(msg) == {"Boolean": True}
    assert msg.body is None


def test_multiple_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, multiple=True)
    msg = parser.parse(
        "Boolean: yes\n"
        "Boolean: y\n"
        "Boolean: on\n"
        "Boolean: true\n"
        "Boolean: 1\n"
        "Boolean: YES\n"
        "Boolean: TRUE\n"
        "Boolean: no\n"
        "Boolean: n\n"
        "Boolean: off\n"
        "Boolean: false\n"
        "Boolean: 0\n"
        "Boolean: NO\n"
        "Boolean: FALSE\n"
    )
    assert dict(msg) == {"Boolean": [True] * 7 + [False] * 7}
    assert msg.body is None


def test_default_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, default="foo")
    msg = parser.parse("Boolean: Off")
    assert dict(msg) == {"Boolean": False}
    assert msg.body is None


def test_missing_default_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, default="foo")
    msg = parser.parse("")
    assert dict(msg) == {"Boolean": "foo"}
    assert msg.body is None


def test_invalid_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL)
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse("Boolean: One\n")
    assert str(excinfo.value) == (
        "Error while parsing 'Boolean': 'One': ValueError: invalid boolean: 'One'"
    )
    assert excinfo.value.name == "Boolean"
    assert excinfo.value.value == "One"
    assert isinstance(excinfo.value.exc_value, ValueError)


def test_bool_and_not_bool() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL)
    parser.add_field("String")
    msg = parser.parse("Boolean: yes\nString: no\n")
    assert dict(msg) == {"Boolean": True, "String": "no"}
    assert msg.body is None


def test_bool_choices_bad_type() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, choices=(False, "foo"))
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse("BOOLEAN: foo\n")
    assert str(excinfo.value) == (
        "Error while parsing 'Boolean': 'foo': ValueError: invalid boolean: 'foo'"
    )
    assert excinfo.value.name == "Boolean"
    assert excinfo.value.value == "foo"
    assert isinstance(excinfo.value.exc_value, ValueError)
    assert "invalid boolean" in str(excinfo.value.exc_value)


def test_native_type() -> None:
    parser = HeaderParser()
    parser.add_field("Number", "No.", type=int, dest="#")
    msg = parser.parse("Number: 42")
    assert dict(msg) == {"#": 42}
    assert msg.body is None


def test_bad_native_type() -> None:
    parser = HeaderParser()
    parser.add_field("Number", "No.", type=int, dest="#")
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse("No.: forty-two")
    assert str(excinfo.value) == (
        "Error while parsing 'Number': 'forty-two': ValueError: "
        + str(excinfo.value.exc_value)
    )
    assert excinfo.value.name == "Number"
    assert excinfo.value.value == "forty-two"
    assert isinstance(excinfo.value.exc_value, ValueError)


def fieldtypeerror_raiser(_: Any) -> None:
    raise FieldTypeError("name", "value", ValueError("foobar"))


def test_fieldtypeerror_raiser() -> None:
    parser = HeaderParser()
    parser.add_field("Foo", type=fieldtypeerror_raiser)
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse("Foo: Bar\n")
    assert str(excinfo.value) == (
        "Error while parsing 'name': 'value': ValueError: foobar"
    )
    assert excinfo.value.name == "name"
    assert excinfo.value.value == "value"
    assert isinstance(excinfo.value.exc_value, ValueError)
    assert str(excinfo.value.exc_value) == "foobar"
