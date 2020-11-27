from   io           import StringIO
import re
import pytest
import headerparser
from   headerparser import scan, scan_file, scan_lines, scan_string

def scan_string_as_file(s, **kwargs):
    return scan(StringIO(s), **kwargs)

def scan_string_as_list(s, **kwargs):
    return scan(s.splitlines(True), **kwargs)

@pytest.fixture(params=[scan_string_as_file, scan_string_as_list, scan_string])
def scanner(request):
    return request.param

def test_simple(scanner):
    assert list(scanner('Foo: red\nBar: green\nBaz: blue\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_empty_body(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\nBar: green\nBaz: blue\n\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_blank_body(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\nBar: green\nBaz: blue\n\n\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '\n')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_body(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'This is a test.',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, 'This is a test.')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_body_extra_blanks(scanner, skip_leading_newlines):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        '\n'
        'This is a test.',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, '\nThis is a test.')]

def test_headerlike_body(scanner):
    assert list(scanner(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Foo: quux\n'
        'Bar: glarch\n'
        'Baz: cleesh\n'
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, 'Foo: quux\nBar: glarch\nBaz: cleesh\n')]

def test_circumcolon_whitespace(scanner):
    assert list(scanner(
        'Key1: Value1\n'
        'Key2 :Value2\n'
        'Key3 : Value3\n'
        'Key4:Value4\n'
    )) == [('Key1', 'Value1'), ('Key2', 'Value2'), ('Key3', 'Value3'),
          ('Key4', 'Value4')]

def test_circumcolon_whitespace_spaceless_separator_regex(scanner):
    assert list(scanner(
        'Key1: Value1\n'
        'Key2 :Value2\n'
        'Key3 : Value3\n'
        'Key4:Value4\n',
        separator_regex=':',
    )) == [('Key1', ' Value1'), ('Key2 ', 'Value2'), ('Key3 ', ' Value3'),
          ('Key4', 'Value4')]

def test_folding(scanner):
    assert list(scanner(
        'Key1: Value1\n'
        '  Folded\n'
        '    More folds\n'
        'Key2: Value2\n'
        '    Folded\n'
        '  Fewer folds\n'
        'Key3: Value3\n'
        '  Key4: Not a real header\n'
        'Key4: \n'
        '\tTab after empty line\n'
        '  \n'
        ' After an "empty" folded line\n'
        'Key5:\n'
        ' After a line without even a space!\n'
    )) == [
        ('Key1', 'Value1\n  Folded\n    More folds'),
        ('Key2', 'Value2\n    Folded\n  Fewer folds'),
        ('Key3', 'Value3\n  Key4: Not a real header'),
        ('Key4', '\n\tTab after empty line\n  \n After an "empty" folded line'),
        ('Key5', '\n After a line without even a space!'),
    ]

def test_no_final_newline(scanner):
    assert list(scanner('Foo: red\nBar: green\nBaz: blue')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_leading_newline(scanner):
    assert list(scanner('\nFoo: red\nBar: green\nBaz: blue\n')) == \
        [(None, 'Foo: red\nBar: green\nBaz: blue\n')]

def test_skip_leading_newlines(scanner):
    assert list(scanner(
        '\nFoo: red\nBar: green\nBaz: blue\n',
        skip_leading_newlines=True,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_cr_terminated():
    assert list(scan_string('Foo: red\rBar: green\rBaz: blue\r')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_crlf_terminated(scanner):
    assert list(scanner('Foo: red\r\nBar: green\r\nBaz: blue\r\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_mixed_terminators():
    assert list(scan_string('Foo: red\nBar: green\rBaz: blue\r\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_mixed_folding():
    assert list(scan_string(
        'Foo: line\n'
        '  feed\n'
        'Bar: carriage\r'
        '  return\r'
        'Baz: CR\r\n'
        '  LF\r\n'
    )) == [
        ('Foo', 'line\n  feed'),
        ('Bar', 'carriage\n  return'),
        ('Baz', 'CR\n  LF'),
    ]

def test_malformed_header(scanner):
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scanner('Foo: red\nBar green\nBaz: blue\n'))
    assert str(excinfo.value) == "Invalid header line encountered: 'Bar green'"
    assert excinfo.value.line == 'Bar green'

def test_unexpected_folding(scanner):
    with pytest.raises(headerparser.UnexpectedFoldingError) as excinfo:
        list(scanner(' Foo: red\nBar green\nBaz: blue\n'))
    assert str(excinfo.value) == (
        "Indented line without preceding header line encountered: ' Foo: red'"
    )
    assert excinfo.value.line == ' Foo: red'

def test_multiple(scanner):
    assert list(scanner(
        'Foo: value1\n'
        'Foo: value2\n'
        'FOO: VALUE3\n'
        'fOO: valueFour\n'
    )) == [
        ('Foo', 'value1'),
        ('Foo', 'value2'),
        ('FOO', 'VALUE3'),
        ('fOO', 'valueFour'),
    ]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_empty(scanner, skip_leading_newlines):
    assert list(scanner('', skip_leading_newlines=skip_leading_newlines)) == []

def test_one_empty_line(scanner):
    assert list(scanner('\n')) == [(None, '')]

def test_one_empty_line_skip_leading_newlines(scanner):
    assert list(scanner('\n', skip_leading_newlines=True)) == []

def test_two_empty_lines(scanner):
    assert list(scanner('\n\n')) == [(None, '\n')]

def test_two_empty_lines_skip_leading_newlines(scanner):
    assert list(scanner('\n\n', skip_leading_newlines=True)) == []

def test_lines_no_ends():
    assert list(scan([
        'Key: value',
        'Folded: hold on',
        '  let me check',
        ' ',
        '  yes',
        '',
        'Newlines will not be added to this body.',
        "So it'll look bad.",
    ])) == [
        ('Key', 'value'),
        ('Folded', 'hold on\n  let me check\n \n  yes'),
        (None, "Newlines will not be added to this body.So it'll look bad."),
    ]

def test_untrimmed_value(scanner):
    assert list(scanner(
        'Leading:   value\n'
        'Trailing: value  \n'
        'Leading-Tab:\tvalue\n'
        'Trailing-Tab:value\t\n'
    )) == [
        ('Leading', 'value'),
        ('Trailing', 'value  '),
        ('Leading-Tab', 'value'),
        ('Trailing-Tab', 'value\t'),
    ]

def test_space_in_name(scanner):
    assert list(scanner('Key Name: value')) == [('Key Name', 'value')]

@pytest.mark.parametrize('separator_regex', [
    r'\s*=\s*',
    re.compile(r'\s*=\s*'),
])
def test_separator_regex(scanner, separator_regex):
    assert list(scanner(
        'Foo = red\nBar =green\nBaz= blue\n',
        separator_regex=separator_regex,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_multi_colon(scanner):
    assert list(scanner('Foo: red : crimson: scarlet\n')) == \
        [('Foo', 'red : crimson: scarlet')]

def test_separator_regex_multi_match(scanner):
    assert list(scanner(
        'Foo = red = crimson=scarlet\n',
        separator_regex=r'\s*=\s*',
    )) == [('Foo', 'red = crimson=scarlet')]

def test_separator_regex_mixed_multi_match(scanner):
    assert list(scanner(
        'Key: Value = foo\nKey = Value: foo\n',
        separator_regex=r'\s*=\s*',
    )) == [('Key: Value', 'foo'), ('Key', 'Value: foo')]

def test_separator_regex_default_separator(scanner):
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scanner('Foo = red\nBar: green\n', separator_regex=r'\s*=\s*'))
    assert str(excinfo.value) == "Invalid header line encountered: 'Bar: green'"
    assert excinfo.value.line == 'Bar: green'

def test_deprecated_scan_lines(mocker):
    mockscan = mocker.patch(
        'headerparser.scanner.scan',
        return_value=mocker.sentinel.OUTPUT,
    )
    with pytest.warns(DeprecationWarning):
        r = scan_lines(mocker.sentinel.INPUT)
    mockscan.assert_called_once_with(mocker.sentinel.INPUT)
    assert r is mocker.sentinel.OUTPUT

def test_deprecated_scan_file(mocker):
    mockscan = mocker.patch(
        'headerparser.scanner.scan',
        return_value=mocker.sentinel.OUTPUT,
    )
    with pytest.warns(DeprecationWarning):
        r = scan_file(mocker.sentinel.INPUT)
    mockscan.assert_called_once_with(mocker.sentinel.INPUT)
    assert r is mocker.sentinel.OUTPUT
