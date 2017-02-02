import pytest
import headerparser
from   headerparser import HeaderParser

def test_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='notfoo')
    parser.add_header('Bar', dest='notbar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'notfoo': 'red', 'notbar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_dest_conflict():
    parser = HeaderParser()
    parser.add_header('Foo', dest='quux')
    with pytest.raises(headerparser.RedefinitionError) as excinfo:
        parser.add_header('Bar', dest='QUUX')
    assert excinfo.value.header is None
    assert excinfo.value.dest == 'QUUX'

def test_header_vs_eq_dest():
    parser = HeaderParser()
    parser.add_header('Foo')
    with pytest.raises(headerparser.RedefinitionError) as excinfo:
        parser.add_header('Bar', dest='Foo')
    assert excinfo.value.header is None
    assert excinfo.value.dest == 'Foo'

def test_header_vs_like_dest():
    parser = HeaderParser()
    parser.add_header('Foo')
    with pytest.raises(headerparser.RedefinitionError) as excinfo:
        parser.add_header('Bar', dest='foo')
    assert excinfo.value.header is None
    assert excinfo.value.dest == 'foo'

def test_header_eq_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='Foo')
    msg = parser.parse_string('foo: red')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None

def test_header_like_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='FOO')
    msg = parser.parse_string('foo: red')
    assert dict(msg) == {'FOO': 'red'}
    assert msg.body is None

def test_header_missing_default_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='FOO', default=42)
    msg = parser.parse_string('')
    assert dict(msg) == {'FOO': 42}
    assert msg.body is None

def test_switched_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='Bar')
    parser.add_header('Bar', dest='Foo')
    msg = parser.parse_string('Foo: foo\nBar: bar\n')
    assert dict(msg) == {'Bar': 'foo', 'Foo': 'bar'}
    assert msg.body is None

def test_one_missing_required_switched_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='Bar', required=True)
    parser.add_header('Bar', dest='Foo', required=True)
    with pytest.raises(headerparser.MissingHeaderError) as excinfo:
        parser.parse_string('Foo: foo\n')
    assert excinfo.value.header == 'Bar'

def test_missing_default_switched_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='Bar', default=42)
    parser.add_header('Bar', dest='Foo', default='17')
    msg = parser.parse_string('')
    assert dict(msg) == {'Bar': 42, 'Foo': '17'}
    assert msg.body is None

def test_one_missing_default_switched_dest():
    parser = HeaderParser()
    parser.add_header('Foo', dest='Bar', default=42)
    parser.add_header('Bar', dest='Foo', default='17')
    msg = parser.parse_string('Foo: 42')
    assert dict(msg) == {'Bar': '42', 'Foo': '17'}
    assert msg.body is None

def test_dest_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', dest='list', multiple=True)
    msg = parser.parse_string('Foo: red\nFoo: green\nFoo: blue')
    assert dict(msg) == {'list': ['red', 'green', 'blue']}
    assert msg.body is None

### dest in input -> UnknownHeaderError
