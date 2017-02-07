import pytest
import headerparser
from   headerparser import HeaderParser

def test_multiname_use_first():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar')
    msg = parser.parse_string('Foo: red')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None

def test_multiname_use_second():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar')
    msg = parser.parse_string('Bar: red')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None

def test_multiname_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar', multiple=True)
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': ['red', 'green'], 'Baz': 'blue'}
    assert msg.body is None

def test_multiname_bad_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar')
    parser.add_header('Baz')
    with pytest.raises(headerparser.DuplicateHeaderError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert excinfo.value.header == 'Foo'

def test_multiname_conflict():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar', multiple=True)
    with pytest.raises(ValueError) as excinfo:
        parser.add_header('Baz', 'BAR')
    assert 'header defined more than once' in str(excinfo.value)

def test_multiname_dest():
    parser = HeaderParser()
    parser.add_header('Foo', 'Bar', dest='Baz')
    msg = parser.parse_string('Bar: red')
    assert dict(msg) == {'Baz': 'red'}
    assert msg.body is None
