from headerparser import scan_string

def test_simple():
    assert list(scan_string('Foo: red\nBar: green\nBaz: blue\n')) == \
        [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'), (None, '')]

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
''') == [('Foo', 'red'), ('Bar', 'green'), ('Baz', 'blue'),
         (None, 'Foo: quux\nBar: glarch\nBaz: cleesh\n')]
