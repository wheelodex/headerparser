import pytest
import headerparser
from   headerparser import BOOL, HeaderParser

@pytest.fixture
def use_as_body(mocker):
    def _use(nd, name, value):
        nd.body = value
    return mocker.Mock(side_effect=_use)

def test_action(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_missing(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Bar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    assert not stub.called

def test_action_type(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, type=BOOL)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: yes\nBar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', True)

def test_action_type_error(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, type=BOOL)
    parser.add_field('Bar')
    with pytest.raises(headerparser.FieldTypeError):
        parser.parse_string('Foo: maybe\nBar: green\n')
    assert not stub.called

def test_action_required(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, required=True)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_required_missing(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, required=True)
    parser.add_field('Bar')
    parser.add_field('Baz')
    with pytest.raises(headerparser.MissingFieldError):
        parser.parse_string('Bar: green\nBaz: blue\n')
    assert not stub.called

def test_action_choices(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, choices=['red', 'green', 'blue'])
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_bad_choice(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, choices=['red', 'green', 'blue'])
    parser.add_field('Bar')
    with pytest.raises(headerparser.InvalidChoiceError):
        parser.parse_string('Foo: taupe\nBar: green\n')
    assert not stub.called

def test_action_unfold(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, unfold=True)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo:  folded\n  text \nBar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'folded text')

def test_action_no_unfold(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo:  folded\n  text \nBar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'folded\n  text ')

def test_action_default(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, default='orange')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Foo: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_default_missing(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, default='orange')
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('Bar: green\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'orange', 'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    assert not stub.called

def test_action_different_case(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('FOO: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_multiname(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', 'Quux', action=stub)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string('quux: red\nBar: green\nBaz: blue\n')
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    stub.assert_called_once_with(msg, 'Foo', 'red')

def test_action_multiple(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo', action=stub, multiple=True)
    parser.add_field('Bar')
    parser.add_field('Baz')
    msg = parser.parse_string(
        'Foo: red\n'
        'Bar: green\n'
        'FOO: purple\n'
        'Baz: blue\n'
        'foo: orange\n'
    )
    assert dict(msg) == {'Bar': 'green', 'Baz': 'blue'}
    assert msg.body is None
    assert stub.call_args_list == [
        mocker.call(msg, 'Foo', 'red'),
        mocker.call(msg, 'Foo', 'purple'),
        mocker.call(msg, 'Foo', 'orange'),
    ]

def test_action_dest(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_field('Foo', action=stub, dest='bar')
    assert '`action` and `dest` are mutually exclusive' in str(excinfo.value)
    assert not stub.called

def test_action_normalized_dest(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    with pytest.raises(ValueError) as excinfo:
        parser.add_field('Foo', action=stub, dest='foo')
    assert '`action` and `dest` are mutually exclusive' in str(excinfo.value)
    assert not stub.called

def test_action_additional(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_additional(action=stub)
    msg = parser.parse_string('Bar: green\nFoo: red\nBaz: blue\n')
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None
    assert stub.call_args_list == [
        mocker.call(msg, 'Bar', 'green'),
        mocker.call(msg, 'Baz', 'blue'),
    ]

def test_action_multiple_additional(mocker):
    stub = mocker.stub()
    parser = HeaderParser()
    parser.add_field('Foo')
    parser.add_additional(action=stub, multiple=True)
    msg = parser.parse_string(
        'Bar: green\n'
        'Foo: red\n'
        'Baz: blue\n'
        'baz: mauve\n'
        'BAR: taupe\n'
    )
    assert dict(msg) == {'Foo': 'red'}
    assert msg.body is None
    assert stub.call_args_list == [
        mocker.call(msg, 'Bar', 'green'),
        mocker.call(msg, 'Baz', 'blue'),
        mocker.call(msg, 'baz', 'mauve'),
        mocker.call(msg, 'BAR', 'taupe'),
    ]

@pytest.mark.parametrize('body', [True, None])
def test_action_set_body_overwritten(body, use_as_body):
    parser = HeaderParser(body=body)
    parser.add_field('Foo', action=use_as_body)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n\nThis is the body.\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body == 'This is the body.\n'
    use_as_body.assert_called_once_with(msg, 'Foo', 'red')

def test_action_set_body_forbidden(use_as_body, mocker):
    parser = HeaderParser(body=False)
    parser.add_field('Foo', action=use_as_body)
    parser.add_field('Bar')
    with pytest.raises(headerparser.BodyNotAllowedError):
        parser.parse_string('Foo: red\nBar: green\n\nThis is the body.\n')
    use_as_body.assert_called_once_with(mocker.ANY, 'Foo', 'red')

@pytest.mark.parametrize('body', [False, None])
def test_action_set_body(body, use_as_body):
    parser = HeaderParser(body=body)
    parser.add_field('Foo', action=use_as_body)
    parser.add_field('Bar')
    msg = parser.parse_string('Foo: red\nBar: green\n')
    assert dict(msg) == {'Bar': 'green'}
    assert msg.body == 'red'
    use_as_body.assert_called_once_with(msg, 'Foo', 'red')

def test_action_set_body_missing(use_as_body, mocker):
    parser = HeaderParser(body=True)
    parser.add_field('Foo', action=use_as_body)
    parser.add_field('Bar')
    with pytest.raises(headerparser.MissingBodyError):
        parser.parse_string('Foo: red\nBar: green\n')
    use_as_body.assert_called_once_with(mocker.ANY, 'Foo', 'red')
