import pytest
from   headerparser import BOOL, HeaderParser, HeaderTypeError

def test_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL)
    msg = parser.parse_string('Boolean: yes\n')
    assert dict(msg) == {'Boolean': True}
    assert msg.body is None

def test_multiple_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, multiple=True)
    msg = parser.parse_string('''\
Boolean: yes
Boolean: y
Boolean: on
Boolean: true
Boolean: 1
Boolean: YES
Boolean: TRUE
Boolean: no
Boolean: n
Boolean: off
Boolean: false
Boolean: 0
Boolean: NO
Boolean: FALSE
''')
    assert dict(msg) == {'Boolean': [True] * 7 + [False] * 7}
    assert msg.body is None

def test_default_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, default='foo')
    msg = parser.parse_string('Boolean: Off')
    assert dict(msg) == {'Boolean': False}
    assert msg.body is None

def test_missing_default_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, default='foo')
    msg = parser.parse_string('')
    assert dict(msg) == {'Boolean': 'foo'}
    assert msg.body is None

def test_invalid_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL)
    with pytest.raises(HeaderTypeError) as excinfo:
        parser.parse_string('Boolean: One\n')
    assert excinfo.value.typename == 'BOOL'
    assert excinfo.value.value == 'One'

def test_bool_and_not_bool():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL)
    parser.add_header('String')
    msg = parser.parse_string('Boolean: yes\nString: no\n')
    assert dict(msg) == {'Boolean': True, 'String': 'no'}
    assert msg.body is None

def test_bool_choices_bad_type():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, choices=(False, 'foo'))
    with pytest.raises(HeaderTypeError) as excinfo:
        parser.parse_string('BOOLEAN: foo\n')
    assert excinfo.value.typename == 'BOOL'
    assert excinfo.value.value == 'foo'
