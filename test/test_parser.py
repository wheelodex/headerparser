import pytest
from   six          import StringIO
import headerparser
from   headerparser import HeaderParser

def test_simple():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_out_of_order():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBaz: blue\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_different_cases():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBAR: green\nbaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_empty_body():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == ''

def test_blank_body():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\n\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == '\n'

def test_body():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n\nThis is a test.')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body == 'This is a test.'

def test_headerlike_body():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
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
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green'}
    assert msg.body is None

def test_required():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', required=True)
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_required_default():
    parser = HeaderParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_field('Foo', required=True, default='Why?')
    assert 'required and default are mutually exclusive' in str(excinfo.value)

def test_required_none():
    parser = HeaderParser()
    parser.add_field('None', required=True, type=lambda _: None)
    msg = parser.parse_string('None: whatever')
    assert dict(msg) == {'None': None}
    assert msg.body is None

def test_missing_required():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', required=True)
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\n')
    assert str(excinfo.value) == "Required header field 'Baz' is not present"
    assert excinfo.value.name == 'Baz'

def test_present_default():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', default=42)
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_missing_default():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', default=42)
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': 42}
    assert msg.body is None

def test_missing_None_default():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz', default=None)
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': 'red', 'Bar': 'green', 'Baz': None}
    assert msg.body is None

def test_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\nfoo : crimson\n')
    assert dict(msg) == {'Foo': ['red', 'magenta', 'crimson'], 'Bar': 'green'}
    assert msg.body is None

def test_one_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body is None

def test_no_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Bar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body is None

def test_bad_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True)
    parser.add_field('Bar')
    with pytest.raises(headerparser.DuplicateFieldError) as excinfo:
        parser.parse_string('Foo: red\nFOO: magenta\nBar: green\nBar: lime\n')
    assert str(excinfo.value) == "Header field 'Bar' occurs more than once"
    assert excinfo.value.name == 'Bar'

def test_default_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, default=42)
    parser.add_field('Bar')
    msg = parser.parse_string('Bar: green\n')
    assert dict(msg) == {'Foo': 42, 'Bar': 'green'}
    assert msg.body is None

def test_present_default_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, default=42)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body is None

def test_present_default_many_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, default=42)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\n')
    assert dict(msg) == {'Foo': ['red', 'magenta'], 'Bar': 'green'}
    assert msg.body is None

def test_required_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, required=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Foo': ['red'], 'Bar': 'green'}
    assert msg.body is None

def test_required_many_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, required=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nFOO: magenta\nBar: green\n')
    assert dict(msg) == {'Foo': ['red', 'magenta'], 'Bar': 'green'}
    assert msg.body is None

def test_missing_required_multiple():
    parser = HeaderParser()
    parser.add_field('Foo', multiple=True, required=True)
    parser.add_field('Bar')
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string('Bar: green\n')
    assert str(excinfo.value) == "Required header field 'Foo' is not present"
    assert excinfo.value.name == 'Foo'

def test_unknown():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.UnknownFieldError) as excinfo:
        parser.parse_string('Foo: red\nBar: green\nQuux: blue\n')
    assert str(excinfo.value) == "Unknown header field 'Quux'"
    assert excinfo.value.name == 'Quux'

def test_empty_input():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('')
    assert dict(msg) == {}
    assert msg.body is None

def test_trailing_whitespace():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red  \nBar: green\n (ish) \nBaz: blue\n   ')
    assert dict(msg) == {
        'Foo': 'red  ',
        'Bar': 'green\n (ish) ',
        'Baz': 'blue\n   ',
    }
    assert msg.body is None

def test_redefinition():
    parser = HeaderParser()
    parser.add_field('Foo')
    with pytest.raises(ValueError) as excinfo:
        parser.add_field('FOO')
    assert 'field defined more than once' in str(excinfo.value)

def test_many_missing_required():
    parser = HeaderParser()
    parser.add_field('Foo', required=True)
    parser.add_field('Bar', required=True)
    parser.add_field('Baz', required=True)
    with pytest.raises(headerparser.MissingFieldError) as excinfo:
        parser.parse_string('')
    assert excinfo.value.name in ('Foo', 'Bar', 'Baz')

def test_unfold():
    parser = HeaderParser()
    parser.add_field('Folded')
    parser.add_field('Unfolded', unfold=True)
    msg = parser.parse_string(
        'Folded: This is\n'
        '   test\n'
        '\ttext.\n'
        'UnFolded: This is\n'
        '   test\n'
        '\ttext.\n'
    )
    assert dict(msg) == {
        "Folded": "This is\n   test\n\ttext.",
        "Unfolded": "This is test text.",
    }
    assert msg.body is None

def test_space_in_name():
    parser = HeaderParser()
    parser.add_field('Key Name')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('key name: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Key Name': 'red', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None

def test_scan_opts_passed(mocker):
    import headerparser.parser
    mocker.patch(
        'headerparser.parser.scan_string',
        wraps=headerparser.parser.scan_string,
    )
    parser = HeaderParser(
        separator_regex=r'\s*:\s*',
        skip_leading_newlines=True,
    )
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    headerparser.parser.scan_string.assert_called_with(
        'Foo: red\nBar: green\nBaz: blue\n',
        separator_regex=r'\s*:\s*',
        skip_leading_newlines=True,
    )

def test_deprecated_parse_lines():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    INPUT = 'Foo: red\nBar: green\nBaz: blue\n'.splitlines(True)
    with pytest.warns(DeprecationWarning):
        msg = parser.parse_lines(INPUT)
    assert msg == parser.parse(INPUT)

def test_deprecated_parse_file():
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_field('Bar')
    parser.add_field('Baz')
    INPUT = StringIO('Foo: red\nBar: green\nBaz: blue\n')
    with pytest.warns(DeprecationWarning):
        msg = parser.parse_file(INPUT)
    INPUT.seek(0)
    assert msg == parser.parse(INPUT)
