from headerparser.util import unfold

def test_unfold_single_line():
    assert unfold('some value') == 'some value'

def test_unfold_two_lines():
    assert unfold('some\nvalue') == 'some value'

def test_unfold_folded_lines():
    assert unfold('some\n value') == 'some value'

def test_unfold_leading_space():
    assert unfold(' some value') == 'some value'

def test_unfold_leading_empty_line():
    assert unfold('\nsome value') == 'some value'

def test_unfold_leading_space_line():
    assert unfold(' \nsome value') == 'some value'

def test_unfold_leading_line_space():
    assert unfold('\n some value') == 'some value'

def test_unfold_trailing_space():
    assert unfold('some value ') == 'some value'

def test_unfold_trailing_empty_line():
    assert unfold('some value\n') == 'some value'

def test_unfold_trailing_line_space():
    assert unfold('some value\n ') == 'some value'

def test_unfold_trailing_space_line():
    assert unfold('some value \n') == 'some value'

def test_unfold_embedded_spaces():
    assert unfold('A period ends a sentence.  It is followed by two spaces.') \
        == 'A period ends a sentence.  It is followed by two spaces.'

def test_unfold_embedded_tabs():
    assert unfold('x\ty\n0\t1\n') == 'x\ty 0\t1'

def test_unfold_varying_indent():
    assert unfold('Value1\n  Folded\n    More folds\n  Fewer folds\n') \
        == 'Value1 Folded More folds Fewer folds'

def test_unfold_tab_indent():
    assert unfold('some\n\tvalue') == 'some value'

def test_unfold_tab_and_space_indent():
    assert unfold('some\n\t value') == 'some value'

def test_unfold_form_field():
    assert unfold('some\n \f value') == 'some \f value'

def test_unfold_spaceful_line():
    assert unfold('some \n  \n value') == 'some value'

def test_unfold_parbreak():
    assert unfold('some\n\nvalue') == 'some value'

def test_unfold_cr():
    assert unfold('some\r value') == 'some value'

def test_unfold_crlf():
    assert unfold('some\r\n value') == 'some value'

def test_unfold_mixed():
    assert unfold('some\nsort\rof\r\nvalue') == 'some sort of value'
