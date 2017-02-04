from headerparser import scan_string

def test_simple():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_empty_body():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '')]

def test_blank_body():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n\n\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '\n')]

def test_body():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n\nThis is a test.')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, 'This is a test.')]

def test_headerlike_body():
    assert list(scan_string('''\
Foo: red
Bar: green
Baz: blue

Foo: quux
Bar: glarch
Baz: cleesh
''')) == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
          (None, 'Foo: quux\nBar: glarch\nBaz: cleesh\n')]

def test_circumcolon_whitespace():
    assert list(scan_string('''\
Key1: Value1
Key2 :Value2
Key3 : Value3
Key4:Value4
''')) == [('Key1', 'Value1'), ('Key2', 'Value2'), ('Key3', 'Value3'),
          ('Key4', 'Value4')]

def test_folding():
    assert list(scan_string('''\
Key1: Value1
  Folded
    More folds
Key2: Value2
    Folded
  Fewer folds
Key3: Value3
  Key4: Not a real header
Key4: 
\tTab after empty line
  
  After an "empty" folded line
Key5:
 After a line without even a space!
''')) == [
    ('Key1', 'Value1\n  Folded\n    More folds'),
    ('Key2', 'Value2\n    Folded\n  Fewer folds'),
    ('Key3', 'Value3\n  Key4: Not a real header'),
    ('Key4', '\n\tTab after empty line\n  \n  After an "empty" folded line'),
    ('Key5', '\n After a line without even a space!'),
]

def test_no_final_newline():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_leading_newline():
    assert list(scan_string('\nFoo: red\nBar: green\nBaz: blue\n')) == \
        [(None, 'Foo: red\nBar: green\nBaz: blue\n')]

def test_cr_terminated():
    assert list(scan_string('Foo: red\rBar: green\rBaz: blue\r')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_crlf_terminated():
    assert list(scan_string('Foo: red\r\nBar: green\r\nBaz: blue\r\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_mixed_terminators():
    assert list(scan_string('Foo: red\nBar: green\rBaz: blue\r\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue')]

def test_mixed_folded():
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

### multiple occurrences of the same header?
