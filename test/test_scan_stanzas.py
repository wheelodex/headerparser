import pytest
from   headerparser import MalformedHeaderError, scan_stanzas_string

def test_simple():
    assert list(scan_stanzas_string(
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
def test_extra_interstitial_blanks(skip_leading_newlines):
    assert list(scan_stanzas_string(
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
def test_trailing_blanks(skip_leading_newlines):
    assert list(scan_stanzas_string(
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

def test_leading_blanks_skip():
    assert list(scan_stanzas_string(
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

def test_leading_blanks_no_skip():
    assert list(scan_stanzas_string(
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

def test_invalid_stanza():
    stanzas = scan_stanzas_string(
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
