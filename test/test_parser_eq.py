import pytest
from headerparser import HeaderParser


def test_eq_empty():
    p1 = HeaderParser()
    p2 = HeaderParser()
    assert p1 == p2


@pytest.mark.parametrize("other", [None, False, True, 42, "", [], {}])
def test_neq_empty_other(other):
    p = HeaderParser()
    assert p != other
    assert other != p


def test_eq_one_field():
    p1 = HeaderParser()
    p1.add_field("Foo")
    p2 = HeaderParser()
    p2.add_field("Foo")
    assert p1 == p2


def test_neq_empty_one_field():
    p1 = HeaderParser()
    p2 = HeaderParser()
    p2.add_field("Foo")
    assert p1 != p2


def test_eq_two_fields():
    p1 = HeaderParser()
    p1.add_field("Foo")
    p1.add_field("Bar")
    p2 = HeaderParser()
    p2.add_field("Foo")
    p2.add_field("Bar")
    assert p1 == p2


def test_eq_out_of_order():
    p1 = HeaderParser()
    p1.add_field("Foo")
    p1.add_field("Bar")
    p2 = HeaderParser()
    p2.add_field("Bar")
    p2.add_field("Foo")
    assert p1 == p2


# multiple, type, action, default, required, custom dest, additional,
# normalizer, body, altnames, altnames with different cases, unfold, choices
