import pytest
from headerparser import BOOL, HeaderParser, InvalidChoiceError


def test_choices() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"])
    msg = parser.parse("Color: green")
    assert dict(msg) == {"Color": "green"}
    assert msg.body is None


def test_invalid_choice() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"])
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse("Color: taupe")
    assert str(excinfo.value) == "'taupe' is not a valid choice for 'Color'"
    assert excinfo.value.name == "Color"
    assert excinfo.value.value == "taupe"


def test_no_choice() -> None:
    parser = HeaderParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_field("Unicorn", choices=[])
    assert str(excinfo.value) == "empty list supplied for choices"


def test_default_choice() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"], default="beige")
    msg = parser.parse("Color: blue")
    assert dict(msg) == {"Color": "blue"}
    assert msg.body is None


def test_missing_default_choice() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"], default="beige")
    msg = parser.parse("")
    assert dict(msg) == {"Color": "beige"}
    assert msg.body is None


def test_unfold_multiple_choices() -> None:
    parser = HeaderParser()
    parser.add_field(
        "Corner",
        choices=["upper left", "upper right", "lower left", "lower right"],
        unfold=True,
        multiple=True,
    )
    msg = parser.parse("Corner: lower right\nCorner: upper\n left\n")
    assert dict(msg) == {"Corner": ["lower right", "upper left"]}
    assert msg.body is None


def test_unfold_indented_choices() -> None:
    parser = HeaderParser()
    parser.add_field(
        "Corner",
        choices=["upper left", "upper right", "lower left", "lower right"],
        unfold=True,
    )
    msg = parser.parse("Corner: upper\n    right")
    assert dict(msg) == {"Corner": "upper right"}
    assert msg.body is None


def test_lower_choices() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"], type=str.lower)
    msg = parser.parse("Color: RED")
    assert dict(msg) == {"Color": "red"}
    assert msg.body is None


def test_lower_invalid_choice() -> None:
    parser = HeaderParser()
    parser.add_field("Color", choices=["red", "green", "blue"], type=str.lower)
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse("Color: MAUVE")
    assert str(excinfo.value) == "'mauve' is not a valid choice for 'Color'"
    assert excinfo.value.name == "Color"
    assert excinfo.value.value == "mauve"


def test_bool_choices() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, choices=(False, "foo"))
    msg = parser.parse("Boolean: N\n")
    assert dict(msg) == {"Boolean": False}
    assert msg.body is None


def test_bool_choices_invalid_choice() -> None:
    parser = HeaderParser()
    parser.add_field("Boolean", type=BOOL, choices=(False, "foo"))
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse("BOOLEAN: Y\n")
    assert str(excinfo.value) == "True is not a valid choice for 'Boolean'"
    assert excinfo.value.name == "Boolean"
    assert excinfo.value.value is True
