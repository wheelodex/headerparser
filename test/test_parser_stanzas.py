import pytest
from   six          import StringIO
import headerparser
from   headerparser import HeaderParser, scan_stanzas_string

def parse_stanzas_string(p, s):
    return p.parse_stanzas_string(s)

def parse_stanzas_string_as_file(p, s):
    return p.parse_stanzas(StringIO(s))

def parse_stanzas_string_as_stream(p, s):
    return p.parse_stanzas_stream(scan_stanzas_string(s))

@pytest.fixture(params=[
    parse_stanzas_string,
    parse_stanzas_string_as_file,
    parse_stanzas_string_as_stream,
])
def pmethod(request):
    return request.param

def test_simple(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\n\n'
        'Baz: sapphire\nBar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\nFoo: fire\n\n'
    )
    assert dict(m1) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert m1.body is None
    assert dict(m2) == {'Foo': 'ruby', 'Bar': 'emerald', 'Baz': 'sapphire'}
    assert m2.body is None
    assert dict(m3) == {'Foo': 'fire', 'Bar': 'earth', 'Baz': 'water'}
    assert m3.body is None

def test_invalid_stanza(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msgs = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\n\n'
        'Baz: sapphire\nBar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\nFoo: fire\nQuux: aether\nCleesh: air\n\n'
        'Baz: ice\nFoo: lightning\nBar: mud\n\n'
    )
    m1 = next(msgs)
    assert dict(m1) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert m1.body is None
    m2 = next(msgs)
    assert dict(m2) == {'Foo': 'ruby', 'Bar': 'emerald', 'Baz': 'sapphire'}
    assert m2.body is None
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        next(msgs)
    assert str(excinfo.value) == "Unknown header field 'Quux'"
    assert excinfo.value.name == 'Quux'

def test_some_required(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo', required=True)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msgs = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\n\n'
        'Baz: sapphire\nBar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\n\n'
        'Baz: ice\nFoo: lightning\nBar: mud\n\n'
    )
    m1 = next(msgs)
    assert dict(m1) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert m1.body is None
    m2 = next(msgs)
    assert dict(m2) == {'Foo': 'ruby', 'Bar': 'emerald', 'Baz': 'sapphire'}
    assert m2.body is None
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        next(msgs)
    assert str(excinfo.value) == "Required header field 'Foo' is not present"
    assert excinfo.value.name == 'Foo'

def test_disjoint_keys(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\n\n'
        'Bar: green\n\n'
        'Baz: blue\n\n'
    )
    assert dict(m1) == {'Foo': 'red'}
    assert m1.body is None
    assert dict(m2) == {'Bar': 'green'}
    assert m2.body is None
    assert dict(m3) == {'Baz': 'blue'}
    assert m3.body is None

def test_overlapping_keys(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\n\n'
        'Bar: green\nFoo: yellow\n\n'
        'Foo: white\nBaz: blue\n\n'
    )
    assert dict(m1) == {'Foo': 'red'}
    assert m1.body is None
    assert dict(m2) == {'Foo': 'yellow', 'Bar': 'green'}
    assert m2.body is None
    assert dict(m3) == {'Foo': 'white', 'Baz': 'blue'}
    assert m3.body is None

def test_multiple(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar', multiple=True)
    parser.add_field('Baz')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\nBar: lime\n\n'
        'Baz: sapphire\nBar: emerald\nBar: jade\nBar: green\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\nFoo: fire\nBar: mud\nBar: land\nBar: solid\n\n'
    )
    assert dict(m1) == {'Foo': 'red', 'Bar': ['green', 'lime'], 'Baz': 'blue'}
    assert m1.body is None
    assert dict(m2) == {
        'Foo': 'ruby',
        'Bar': ['emerald', 'jade', 'green'],
        'Baz': 'sapphire',
    }
    assert m2.body is None
    assert dict(m3) == {
        'Foo': 'fire',
        'Bar': ['earth', 'mud', 'land', 'solid'],
        'Baz': 'water',
    }
    assert m3.body is None

def test_default(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', default='DEF')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\n\n'
        'Bar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\nFoo: fire\n\n'
    )
    assert dict(m1) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert m1.body is None
    assert dict(m2) == {'Foo': 'ruby', 'Bar': 'emerald', 'Baz': 'DEF'}
    assert m2.body is None
    assert dict(m3) == {'Foo': 'fire', 'Bar': 'earth', 'Baz': 'water'}
    assert m3.body is None

def test_default_inverted(pmethod):
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', default='DEF')
    m1, m2, m3 = pmethod(
        parser,
        'Foo: red\nBar: green\n\n'
        'Baz: sapphire\nBar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nFoo: fire\n\n'
    )
    assert dict(m1) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'DEF'}
    assert m1.body is None
    assert dict(m2) == {'Foo': 'ruby', 'Bar': 'emerald', 'Baz': 'sapphire'}
    assert m2.body is None
    assert dict(m3) == {'Foo': 'fire', 'Bar': 'earth', 'Baz': 'DEF'}
    assert m3.body is None

def test_body_true(pmethod):
    parser = HeaderParser(body=True)
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msgs = pmethod(
        parser,
        'Foo: red\nBar: green\nBaz: blue\n\n'
        'Baz: sapphire\nBar: emerald\nFoo: ruby\n\n'
        'Bar: earth\nBaz: water\nFoo: fire\n\n'
    )
    with pytest.raises(headerparser.MissingBodyError):
        next(msgs)
