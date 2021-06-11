import pytest
import headerparser
from headerparser import HeaderParser


def test_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional()
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_many_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional()
    msg = parser.parse_string(
        "Foo: red\nBar: green\nBaz: blue\nQUUX: purple\nglarch: orange\n"
    )
    assert dict(msg) == {
        "Foo": "red",
        "Bar": "green",
        "Baz": "blue",
        "QUUX": "purple",
        "glarch": "orange",
    }
    assert msg.body is None


def test_intermixed_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional()
    msg = parser.parse_string(
        "QUUX: purple\nBar: green\nglarch: orange\nFoo: red\nBaz: blue\n"
    )
    assert dict(msg) == {
        "Foo": "red",
        "Bar": "green",
        "Baz": "blue",
        "QUUX": "purple",
        "glarch": "orange",
    }
    assert msg.body is None


def test_additional_only():
    parser = HeaderParser()
    parser.add_additional()
    msg = parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Baz": "blue"}
    assert msg.body is None


def test_dest_additional():
    parser = HeaderParser()
    parser.add_field("Foo", dest="dest")
    parser.add_field("Bar")
    with pytest.raises(ValueError) as excinfo:
        parser.add_additional()
    assert "add_additional and `dest` are mutually exclusive" in str(excinfo.value)


def test_additional_dest():
    parser = HeaderParser()
    parser.add_additional()
    parser.add_field("Foo")
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Bar", dest="dest")
    assert "add_additional and `dest` are mutually exclusive" in str(excinfo.value)


def test_additional_bad_named_multiple():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional()
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string("Foo: red\nFOO: magenta\nBar: green\n")
    assert str(excinfo.value) == "Header field 'Foo' occurs more than once"
    assert excinfo.value.name == "Foo"


def test_additional_named_multiple():
    parser = HeaderParser()
    parser.add_field("Foo", multiple=True)
    parser.add_additional()
    msg = parser.parse_string("Foo: red\nFOO: magenta\nBar: green\n")
    assert dict(msg) == {"Foo": ["red", "magenta"], "Bar": "green"}
    assert msg.body is None


def test_additional_bad_multiple():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional()
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\nBar: lime\n")
    assert str(excinfo.value) == "Header field 'Bar' occurs more than once"
    assert excinfo.value.name == "Bar"


def test_additional_bad_multiple_cases():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional()
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\nBAR: lime\n")
    assert str(excinfo.value) == "Header field 'BAR' occurs more than once"
    assert excinfo.value.name == "BAR"


def test_multiple_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional(multiple=True)
    msg = parser.parse_string("Foo: red\nBar: green\nBAR: lime\n")
    assert dict(msg) == {"Foo": "red", "Bar": ["green", "lime"]}
    assert msg.body is None


def test_one_multiple_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional(multiple=True)
    msg = parser.parse_string("Foo: red\nBAR: lime\n")
    assert dict(msg) == {"Foo": "red", "BAR": ["lime"]}
    assert msg.body is None


def test_multiple_additional_bad_named_multiple():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(multiple=True)
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\nBaz: blue\nFOO: magenta\n")
    assert str(excinfo.value) == "Header field 'Foo' occurs more than once"
    assert excinfo.value.name == "Foo"


def test_additional_missing_named():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional()
    msg = parser.parse_string("Baz: blue\nQUUX: purple\nglarch: orange\n")
    assert dict(msg) == {"Baz": "blue", "QUUX": "purple", "glarch": "orange"}
    assert msg.body is None


def test_additional_missing_required_named():
    parser = HeaderParser()
    parser.add_field("Foo", required=True)
    parser.add_field("Bar")
    parser.add_additional()
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string("Baz: blue\nQUUX: purple\nglarch: orange\n")
    assert str(excinfo.value) == "Required header field 'Foo' is not present"
    assert excinfo.value.name == "Foo"


def test_missing_additional():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional()
    msg = parser.parse_string("Foo: red\nBar: green\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green"}
    assert msg.body is None


def test_additional_type():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(type=int)
    msg = parser.parse_string("Foo: 1\nBar: 2\nBaz: 3\n")
    assert dict(msg) == {"Foo": "1", "Bar": "2", "Baz": 3}
    assert msg.body is None


def test_additional_bad_type():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(type=int)
    with pytest.raises(headerparser.FieldTypeError) as excinfo:
        parser.parse_string("Foo: 1\nBar: 2\nBaz: three\n")
    assert str(excinfo.value) == (
        "Error while parsing 'Baz': 'three': ValueError: "
        + str(excinfo.value.exc_value)
    )
    assert excinfo.value.name == "Baz"
    assert excinfo.value.value == "three"
    assert isinstance(excinfo.value.exc_value, ValueError)


def test_additional_choices():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(choices=["red", "green", "blue"])
    msg = parser.parse_string("Foo: mauve\nBar: red\nBaz: green\nQuux: blue\n")
    assert dict(msg) == {
        "Foo": "mauve",
        "Bar": "red",
        "Baz": "green",
        "Quux": "blue",
    }
    assert msg.body is None


def test_additional_bad_choices():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(choices=["red", "green", "blue"])
    with pytest.raises(headerparser.InvalidChoiceError) as excinfo:
        parser.parse_string("Foo: mauve\nBar: red\nBaz: green\nQuux: taupe\n")
    assert str(excinfo.value) == "'taupe' is not a valid choice for 'Quux'"
    assert excinfo.value.name == "Quux"
    assert excinfo.value.value == "taupe"


def test_additional_unfold():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_additional(unfold=True)
    msg = parser.parse_string(
        "Foo: This is\n"
        "   test\n"
        "  text.\n"
        "Bar: This is\n"
        "   test\n"
        "  text.\n"
    )
    assert dict(msg) == {
        "Foo": "This is\n   test\n  text.",
        "Bar": "This is test text.",
    }
    assert msg.body is None


def test_bad_additional_dest():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    with pytest.raises(TypeError):
        parser.add_additional(dest="somewhere")


def test_bad_additional_required():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    with pytest.raises(TypeError):
        parser.add_additional(required=True)


def test_bad_additional_default():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    with pytest.raises(TypeError):
        parser.add_additional(default="")


def test_additional_multiname():
    parser = HeaderParser()
    parser.add_field("Foo", "Oof")
    parser.add_field("Bar", "Baz")
    parser.add_additional()
    msg = parser.parse_string("Oof: red\nBar: green\nQuux: blue\n")
    assert dict(msg) == {"Foo": "red", "Bar": "green", "Quux": "blue"}
    assert msg.body is None


def test_additional_off():
    parser = HeaderParser()
    parser.add_field("Foo")
    parser.add_field("Bar")
    parser.add_additional(False)
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        parser.parse_string("Foo: red\nBar: green\nBaz: blue\n")
    assert str(excinfo.value) == "Unknown header field 'Baz'"
    assert excinfo.value.name == "Baz"
