import pytest
import headerparser
from   headerparser import HeaderParser

def test_require_body():
    parser = HeaderParser(body=True)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'This space intentionally left nonblank.\n'
    )
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == 'This space intentionally left nonblank.\n'

def test_empty_required_body():
    parser = HeaderParser(body=True)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == ''

def test_missing_required_body():
    parser = HeaderParser(body=True)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.MissingBodyError):
        parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')

def test_forbid_body():
    parser = HeaderParser(body=False)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_empty_forbidden_body():
    parser = HeaderParser(body=False)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.BodyNotAllowedError):
        parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n')

def test_present_forbidden_body():
    parser = HeaderParser(body=False)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.BodyNotAllowedError):
        parser.parse_string(
            'Foo: red\n'
            'Bar: green\n'
            'Baz: blue\n'
            '\n'
            'This space intentionally left nonblank.\n'
        )

def test_headers_as_required_body():
    parser = HeaderParser(body=True)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('\nFoo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {}
    assert msg.body == 'Foo: red\nBar: green\nBaz: blue\n'

def test_headers_as_forbidden_body():
    parser = HeaderParser(body=False)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.BodyNotAllowedError):
        parser.parse_string('\nFoo: red\nBar: green\nBaz: blue\n')

def test_required_body_only():
    parser = HeaderParser(body=True)
    msg = parser.parse_string('\nFoo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {}
    assert msg.body == 'Foo: red\nBar: green\nBaz: blue\n'

def test_body_as_unknown_headers():
    parser = HeaderParser(body=True)
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert excinfo.value.name == 'Foo'

def test_require_body_all_empty():
    parser = HeaderParser(body=True)
    msg = parser.parse_string('\n')
    assert dict(msg) == {}
    assert msg.body == ''

def test_forbid_body_all_empty():
    parser = HeaderParser(body=False)
    with pytest.raises(headerparser.BodyNotAllowedError):
        parser.parse_string('\n\n')