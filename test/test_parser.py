import pytest
import headerparser
from   headerparser import HeaderParser

def test_simple():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_out_of_order():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBaz: blue\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_different_cases():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBAR: green\nbaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_empty_body():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == ''

def test_blank_body():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == '\n'

def test_body():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\nThis is a test.')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == 'This is a test.'

def test_headerlike_body():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('''\
Foo: red
Bar: green
Baz: blue

Foo: quux
Bar: glarch
Baz: cleesh
''')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == 'Foo: quux\nBar: glarch\nBaz: cleesh\n'

def test_missing():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green'}
    assert msg.body == None

def test_required():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', required=True)
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_required_default():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', required=True, default='This will never be used.')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_missing_required():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', required=True)
    with pytest.raises(headerparser.MissingHeaderError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\n')
    assert excinfo.value.header == 'Baz'

def test_missing_required_default():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', required=True, default='still required')
    with pytest.raises(headerparser.MissingHeaderError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\n')
    assert excinfo.value.header == 'Baz'

def test_present_default():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', default=42)
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == None

def test_missing_default():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', default=42)
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 42}
    assert msg.body == None

def test_missing_None_default():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz', default=None)
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': None}
    assert msg.body == None

def test_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\nfoo : crimson\n')
    assert dict(msg) == {'Foo': ['red', 'magenta', 'crimson'], 'Bar': 'green'}
    assert msg.body == None

def test_one_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body == None

def test_no_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True)
    parser.add_header('Bar')
    msg = parser.parse_string('Bar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body == None

def test_bad_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True)
    parser.add_header('Bar')
    with pytest.raises(headerparser.DuplicateHeaderError) as excinfo:
        parser.parse_string('Foo: red\nFOO: magenta\nBar: green\nBar: lime\n')
    assert excinfo.value.header == 'Bar'

def test_default_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, default=42)
    parser.add_header('Bar')
    msg = parser.parse_string('Bar: green\n')
    assert dict(msg) == {'Foo': 42, 'Bar': 'green'}
    assert msg.body == None

def test_present_default_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, default=42)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body == None

def test_present_default_many_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, default=42)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\n')
    assert dict(msg) == {'Foo': ['red', 'magenta'], 'Bar': 'green'}
    assert msg.body == None

def test_required_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, required=True)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body == None

def test_required_many_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, required=True)
    parser.add_header('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\n')
    assert dict(msg) == {'Foo': ['red', 'magenta'], 'Bar': 'green'}
    assert msg.body == None

def test_missing_required_multiple():
    parser = HeaderParser()
    parser.add_header('Foo', multiple=True, required=True)
    parser.add_header('Bar')
    with pytest.raises(headerparser.MissingHeaderError) as excinfo:
        parser.parse_string('Bar: green\n')
    assert excinfo.value.header == 'Foo'

def test_unknown():
    parser = HeaderParser()
    parser.add_header('Foo')
    parser.add_header('Bar')
    parser.add_header('Baz')
    with pytest.raises(headerparser.UnknownHeaderError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\nQuux: blue\n')
    assert excinfo.value.header == 'Quux'
