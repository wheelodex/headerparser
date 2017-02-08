import pytest
from   headerparser import NormalizedDict

def test_empty():
    nd = NormalizedDict()
    assert dict(nd) == {}
    assert nd.body is None
    assert len(nd) == 0
    assert not bool(nd)

def test_one():
    nd = NormalizedDict({"Foo": "bar"})
    assert dict(nd) == {"Foo": "bar"}
    assert nd.body is None
    assert len(nd) == 1
    assert bool(nd)

def test_get_cases():
    nd = NormalizedDict({"Foo": "bar"})
    assert nd["Foo"] == "bar"
    assert nd["Foo"] == nd["foo"] == nd["FOO"] == nd["fOO"]

def test_set():
    nd = NormalizedDict()
    assert dict(nd) == {}
    nd["Foo"] = "bar"
    assert dict(nd) == {"Foo": "bar"}
    assert nd["Foo"] == "bar"
    assert nd["Foo"] == nd["foo"] == nd["FOO"] == nd["fOO"]
    nd["fOO"] = "quux"
    assert dict(nd) == {"fOO": "quux"}
    assert nd["Foo"] == "quux"
    assert nd["Foo"] == nd["foo"] == nd["FOO"] == nd["fOO"]

def test_del():
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"})
    del nd["Foo"]
    assert dict(nd) == {"Bar": "FOO"}
    del nd["BAR"]
    assert dict(nd) == {}

def test_del_nexists():
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"})
    with pytest.raises(KeyError):
        del nd["Baz"]

def test_eq_empty():
    nd = NormalizedDict()
    nd2 = NormalizedDict()
    assert nd == nd2

def test_eq_cases():
    nd = NormalizedDict({"Foo": "bar"})
    nd2 = NormalizedDict({"fOO": "bar"})
    assert nd == nd2

def test_neq():
    assert NormalizedDict({"Foo": "bar"}) != NormalizedDict({"Foo": "BAR"})

def test_normalized():
    nd = NormalizedDict({"Foo": "BAR"})
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"foo": "BAR"}
    assert nd.body is None
    assert nd == nd2

def test_normalized_with_body():
    nd = NormalizedDict({"Foo": "BAR"}, body='Glarch.')
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"foo": "BAR"}
    assert nd.body == 'Glarch.'
    assert nd == nd2

def test_normalized_dict():
    nd = NormalizedDict({"Foo": "BAR"})
    nd2 = nd.normalized_dict()
    assert isinstance(nd2, dict)
    assert nd2 == {"foo": "BAR"}

def test_eq_dict():
    nd = NormalizedDict({"Foo": "BAR"})
    assert nd == {"Foo": "BAR"}
    assert {"Foo": "BAR"} == nd
    assert nd == {"FOO": "BAR"}
    assert {"FOO": "BAR"} == nd
    assert nd == {"foo": "BAR"}
    assert {"foo": "BAR"} == nd
    assert nd != {"Foo": "bar"}
    assert {"Foo": "bar"} != nd

def test_body_neq_dict():
    nd = NormalizedDict({"Foo": "BAR"}, body='')
    assert nd != {"Foo": "BAR"}
    assert {"Foo": "BAR"} != nd

def test_eq_body():
    nd = NormalizedDict({"Foo": "bar"}, body='')
    nd2 = NormalizedDict({"fOO": "bar"}, body='')
    assert nd == nd2

def test_neq_body():
    nd = NormalizedDict({"Foo": "bar"}, body='yes')
    nd2 = NormalizedDict({"fOO": "bar"}, body='no')
    assert nd != nd2

def test_neq_none():
    assert NormalizedDict() != None
    assert None != NormalizedDict()

def test_neq_bool():
    assert NormalizedDict() != False
    assert False != NormalizedDict()

def test_neq_int():
    assert NormalizedDict() != 42
    assert 42 != NormalizedDict()

def test_init_list():
    nd = NormalizedDict([("Foo", "bar"), ("Bar", "baz"), ("FOO", "quux")])
    assert dict(nd) == {"FOO": "quux", "Bar": "baz"}

### different normalizers (identity, hyphens=underscores, titlecase?, etc.)
### eq with different normalizers
### copy
