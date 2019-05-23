import pytest
from   six          import StringIO
from   headerparser import MalformedHeaderError, scan_stanzas, \
                            scan_stanzas_string

def scan_stanzas_string_as_file(s, **kwargs):
    return scan_stanzas(StringIO(s), **kwargs)

def scan_stanzas_string_as_list(s, **kwargs):
    return scan_stanzas(s.splitlines(True), **kwargs)

@pytest.fixture(params=[
    scan_stanzas_string_as_file,
    scan_stanzas_string_as_list,
    scan_stanzas_string,
])
def scanner(request):
    return request.param

def test_simple(scanner):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        'Blue: foo\n'
        'Red: bar\n'
        'Green: baz\n'
    )) == [
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')],
        [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')],
        [('Blue', 'foo'), ('Red', 'bar'), ('Green', 'baz')],
    ]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_extra_interstitial_blanks(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        '\n'
        '\n'
        'Blue: foo\n'
        'Red: bar\n'
        'Green: baz\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')],
        [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')],
        [('Blue', 'foo'), ('Red', 'bar'), ('Green', 'baz')],
    ]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_trailing_blanks(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        'Blue: foo\n'
        'Red: bar\n'
        'Green: baz\n',
        '\n'
        '\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')],
        [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')],
        [('Blue', 'foo'), ('Red', 'bar'), ('Green', 'baz')],
    ]

def test_leading_blanks_skip(scanner):
    assert list(scanner(
        '\n'
        '\n'
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        'Blue: foo\n'
        'Red: bar\n'
        'Green: baz\n',
        skip_leading_newlines=True,
    )) == [
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')],
        [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')],
        [('Blue', 'foo'), ('Red', 'bar'), ('Green', 'baz')],
    ]

def test_leading_blanks_no_skip(scanner):
    assert list(scanner(
        '\n'
        '\n'
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        'Blue: foo\n'
        'Red: bar\n'
        'Green: baz\n',
        skip_leading_newlines=False,
    )) == [
        [],
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')],
        [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')],
        [('Blue', 'foo'), ('Red', 'bar'), ('Green', 'baz')],
    ]

def test_invalid_stanza(scanner):
    stanzas = scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Quux: ruby\n'
        'Glarch: sapphire\n'
        'Cleesh: garnet\n'
        '\n'
        'Blue: foo\n'
        "Wait, this isn't a header.\n"
        'Green: baz\n'
    )
    assert next(stanzas) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]
    assert next(stanzas) \
        == [('Quux', 'ruby'), ('Glarch', 'sapphire'), ('Cleesh', 'garnet')]
    with pytest.raises(MalformedHeaderError) as excinfo:
        next(stanzas)
    assert str(excinfo.value) == (
        "Invalid header line encountered: \"Wait, this isn't a header.\""
    )

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_empty(scanner, skip_leading_newlines):
    assert list(scanner('', skip_leading_newlines=skip_leading_newlines)) == []

def test_all_blanks_skip(scanner):
    assert list(scanner('\n\n', skip_leading_newlines=True)) == []

def test_all_blanks_no_skip(scanner):
    assert list(scanner('\n\n', skip_leading_newlines=False)) == [[]]
