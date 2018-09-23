import re
import pytest
import headerparser
from   headerparser import scan_string, scan_lines

def test_simple():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_empty_body(skip_leading_newlines):
    assert list(scan_string(
        'Foo: red\nBar: green\nBaz: blue\n\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_blank_body(skip_leading_newlines):
    assert list(scan_string(
        'Foo: red\nBar: green\nBaz: blue\n\n\n',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '\n')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_body(skip_leading_newlines):
    assert list(scan_string(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'This is a test.',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, 'This is a test.')]

@pytest.mark.parametrize('skip_leading_newlines', [True, False])
def test_body_extra_blanks(skip_leading_newlines):
    assert list(scan_string(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        '\n'
        'This is a test.',
        skip_leading_newlines=skip_leading_newlines,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, '\nThis is a test.')]

def test_headerlike_body():
    assert list(scan_string(
        'Foo: red\n'
        'Bar: green\n'
        'Baz: blue\n'
        '\n'
        'Foo: quux\n'
        'Bar: glarch\n'
        'Baz: cleesh\n'
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
           (None, 'Foo: quux\nBar: glarch\nBaz: cleesh\n')]

def test_circumcolon_whitespace():
    assert list(scan_string(
        'Key1: Value1\n'
        'Key2 :Value2\n'
        'Key3 : Value3\n'
        'Key4:Value4\n'
    )) == [('Key1', 'Value1'), ('Key2', 'Value2'), ('Key3', 'Value3'),
          ('Key4', 'Value4')]

def test_circumcolon_whitespace_spaceless_separator_regex():
    assert list(scan_string(
        'Key1: Value1\n'
        'Key2 :Value2\n'
        'Key3 : Value3\n'
        'Key4:Value4\n',
        separator_regex=':',
    )) == [('Key1', ' Value1'), ('Key2 ', 'Value2'), ('Key3 ', ' Value3'),
          ('Key4', 'Value4')]

def test_folding():
    assert list(scan_string(
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

def test_no_final_newline():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_leading_newline():
    assert list(scan_string('\nFoo: red\nBar: green\nBaz: blue\n')) == \
        [(None, 'Foo: red\nBar: green\nBaz: blue\n')]

def test_skip_leading_newlines():
    assert list(scan_string(
        '\nFoo: red\nBar: green\nBaz: blue\n',
        skip_leading_newlines=True,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_cr_terminated():
    assert list(scan_string('Foo: red\rBar: green\rBaz: blue\r')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_crlf_terminated():
    assert list(scan_string('Foo: red\r\nBar: green\r\nBaz: blue\r\n')) == \
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

def test_malformed_header():
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scan_string('Foo: red\nBar green\nBaz: blue\n'))
    assert excinfo.value.line == 'Bar green'

def test_unexpected_folding():
    with pytest.raises(headerparser.UnexpectedFoldingError) as excinfo:
        list(scan_string(' Foo: red\nBar green\nBaz: blue\n'))
    assert excinfo.value.line == ' Foo: red'

def test_multiple():
    assert list(scan_string(
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
def test_empty(skip_leading_newlines):
    assert list(scan_string('', skip_leading_newlines=skip_leading_newlines)) \
        == []

def test_one_empty_line():
    assert list(scan_string('\n')) == [(None, '')]

def test_one_empty_line_skip_leading_newlines():
    assert list(scan_string('\n', skip_leading_newlines=True)) == []

def test_two_empty_lines():
    assert list(scan_string('\n\n')) == [(None, '\n')]

def test_two_empty_lines_skip_leading_newlines():
    assert list(scan_string('\n\n', skip_leading_newlines=True)) == []

def test_lines_no_ends():
    assert list(scan_lines([
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

def test_untrimmed_value():
    assert list(scan_string(
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

def test_space_in_name():
    assert list(scan_string('Key Name: value')) == [('Key Name', 'value')]

@pytest.mark.parametrize('separator_regex', [
    r'\s*=\s*',
    re.compile(r'\s*=\s*'),
])
def test_separator_regex(separator_regex):
    assert list(scan_string(
        'Foo = red\nBar =green\nBaz= blue\n',
        separator_regex=separator_regex,
    )) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_multi_colon():
    assert list(scan_string('Foo: red : crimson: scarlet\n')) == \
        [('Foo', 'red : crimson: scarlet')]

def test_separator_regex_multi_match():
    assert list(scan_string(
        'Foo = red = crimson=scarlet\n',
        separator_regex=r'\s*=\s*',
    )) == [('Foo', 'red = crimson=scarlet')]

def test_separator_regex_mixed_multi_match():
    assert list(scan_string(
        'Key: Value = foo\nKey = Value: foo\n',
        separator_regex=r'\s*=\s*',
    )) == [('Key: Value', 'foo'), ('Key', 'Value: foo')]

def test_separator_regex_default_separator():
    with pytest.raises(headerparser.MalformedHeaderError) as excinfo:
        list(scan_string('Foo = red\nBar: green\n', separator_regex=r'\s*=\s*'))
    assert excinfo.value.line == 'Bar: green'
