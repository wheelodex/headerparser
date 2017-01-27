import pytest
from   headerparser import BOOL, HeaderParser, InvalidChoiceError

def test_choices():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red', 'green', 'blue'])
    msg = parser.parse_string('Color: green')
    assert dict(msg) == {'Color': 'green'}
    assert msg.body is None

def test_invalid_choice():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red', 'green', 'blue'])
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse_string('Color: taupe')
    assert excinfo.value.header == 'Color'
    assert excinfo.value.value == 'taupe'

def test_no_choice():
    parser = HeaderParser()
    with pytest.raises(ValueError):
        parser.add_header('Unicorn', choices=[])

def test_default_choice():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red','green','blue'], default='beige')
    msg = parser.parse_string('Color: blue')
    assert dict(msg) == {'Color': 'blue'}
    assert msg.body is None

def test_missing_default_choice():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red','green','blue'], default='beige')
    msg = parser.parse_string('')
    assert dict(msg) == {'Color': 'beige'}
    assert msg.body is None

def test_unfold_multiple_choices():
    parser = HeaderParser()
    parser.add_header('Corner', choices=[
        'upper left', 'upper right', 'lower left', 'lower right'
    ], unfold=True, multiple=True)
    msg = parser.parse_string('Corner: lower right\nCorner: upper\n left\n')
    assert dict(msg) == {'Corner': ['lower right', 'upper left']}
    assert msg.body is None

def test_unfold_indented_invalid_choice():
    parser = HeaderParser()
    parser.add_header('Corner', choices=[
        'upper left', 'upper right', 'lower left', 'lower right'
    ], unfold=True)
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse_string('Corner: upper\n    right')
    assert excinfo.value.header == 'Corner'
    assert excinfo.value.value == 'upper    right'

def test_lower_choices():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red', 'green', 'blue'], type=str.lower)
    msg = parser.parse_string('Color: RED')
    assert dict(msg) == {'Color': 'red'}
    assert msg.body is None

def test_lower_invalid_choice():
    parser = HeaderParser()
    parser.add_header('Color', choices=['red', 'green', 'blue'], type=str.lower)
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse_string('Color: MAUVE')
    assert excinfo.value.header == 'Color'
    assert excinfo.value.value == 'mauve'

def test_bool_choices():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, choices=(False, 'foo'))
    msg = parser.parse_string('Boolean: N\n')
    assert dict(msg) == {'Boolean': False}
    assert msg.body is None

def test_bool_choices_invalid_choice():
    parser = HeaderParser()
    parser.add_header('Boolean', type=BOOL, choices=(False, 'foo'))
    with pytest.raises(InvalidChoiceError) as excinfo:
        parser.parse_string('BOOLEAN: Y\n')
    assert excinfo.value.header == 'Boolean'
    assert excinfo.value.value is True
