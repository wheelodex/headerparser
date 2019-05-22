import pytest
import headerparser
from   headerparser import HeaderParser

def test_multiname_use_first():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar')
    msg = parser.parse_string('Foo: red')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None

def test_multiname_use_second():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar')
    msg = parser.parse_string('Bar: red')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None

def test_multiname_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar', multiple=True)
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': ['red', 'green'], 'Baz': 'blue'}
    assert msg.body is None

def test_multiname_bad_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert str(excinfo.value) == "Header field 'Foo' occurs more than once"
    assert excinfo.value.name == 'Foo'

def test_multiname_conflict():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar', multiple=True)
    with pytest.raises(ValueError) as excinfo:
        parser.add_field('Baz', 'BAR')
    assert 'field defined more than once' in str(excinfo.value)

def test_multiname_dest():
    parser = HeaderParser()
    parser.add_field('Foo', 'Bar', dest='Baz')
    msg = parser.parse_string('Bar: red')
    assert dict(msg) == {'Baz': 'red'}
    assert msg.body is None
