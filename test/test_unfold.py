import pytest
from headerparser import unfold


@pytest.mark.parametrize(
    "sin,sout",
    [
        ("some value", "some value"),
        ("some\nvalue", "some value"),
        ("some\n value", "some value"),
        (" some value", "some value"),
        ("\nsome value", "some value"),
        (" \nsome value", "some value"),
        ("\n some value", "some value"),
        ("some value ", "some value"),
        ("some value\n", "some value"),
        ("some value\n ", "some value"),
        ("some value \n", "some value"),
        (
            "A period ends a sentence.  It is followed by two spaces.",
            "A period ends a sentence.  It is followed by two spaces.",
        ),
        ("x\ty\n0\t1\n", "x\ty 0\t1"),
        (
            "Value1\n  Folded\n    More folds\n  Fewer folds\n",
            "Value1 Folded More folds Fewer folds",
        ),
        ("some\n\tvalue", "some value"),
        ("some\n\t value", "some value"),
        ("some\n \f value", "some \f value"),
        ("some \n  \n value", "some value"),
        ("some\n\nvalue", "some value"),
        ("some\r value", "some value"),
        ("some\r\n value", "some value"),
        ("some\nsort\rof\r\nvalue", "some sort of value"),
    ],
)
def test_unfold_single_line(sin, sout):
    assert unfold(sin) == sout
