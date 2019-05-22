import pytest
from   headerparser import BOOL, HeaderParser, FieldTypeError

def test_bool():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL)
    msg = parser.parse_string('Boolean: yes\n')
    assert dict(msg) == {'Boolean': True}
    assert msg.body is None

def test_multiple_bool():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL, multiple=True)
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
    parser.add_field('Boolean', type=BOOL, default='foo')
    msg = parser.parse_string('Boolean: Off')
    assert dict(msg) == {'Boolean': False}
    assert msg.body is None

def test_missing_default_bool():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL, default='foo')
    msg = parser.parse_string('')
    assert dict(msg) == {'Boolean': 'foo'}
    assert msg.body is None

def test_invalid_bool():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL)
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse_string('Boolean: One\n')
    assert str(excinfo.value) == (
        "Error while parsing 'Boolean': 'One': ValueError: invalid boolean:"
        " 'One'"
    )
    assert excinfo.value.name == 'Boolean'
    assert excinfo.value.value == 'One'
    assert isinstance(excinfo.value.exc_value, ValueError)

def test_bool_and_not_bool():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL)
    parser.add_field('String')
    msg = parser.parse_string('Boolean: yes\nString: no\n')
    assert dict(msg) == {'Boolean': True, 'String': 'no'}
    assert msg.body is None

def test_bool_choices_bad_type():
    parser = HeaderParser()
    parser.add_field('Boolean', type=BOOL, choices=(False, 'foo'))
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse_string('BOOLEAN: foo\n')
    assert str(excinfo.value) == (
        "Error while parsing 'Boolean': 'foo': ValueError: invalid boolean:"
        " 'foo'"
    )
    assert excinfo.value.name == 'Boolean'
    assert excinfo.value.value == 'foo'
    assert isinstance(excinfo.value.exc_value, ValueError)
    assert 'invalid boolean' in str(excinfo.value.exc_value)

def test_native_type():
    parser = HeaderParser()
    parser.add_field('Number', 'No.', type=int, dest='#')
    msg = parser.parse_string('Number: 42')
    assert dict(msg) == {"#": 42}
    assert msg.body is None

def test_bad_native_type():
    parser = HeaderParser()
    parser.add_field('Number', 'No.', type=int, dest='#')
    with pytest.raises(FieldTypeError) as excinfo:
        parser.parse_string('No.: forty-two')
    assert str(excinfo.value) == (
        "Error while parsing 'Number': 'forty-two': ValueError: "
        + str(excinfo.value.exc_value)
    )
    assert excinfo.value.name == 'Number'
    assert excinfo.value.value == 'forty-two'
    assert isinstance(excinfo.value.exc_value, ValueError)
