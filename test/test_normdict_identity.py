import pytest
from   headerparser import NormalizedDict

def identity(s): return s

def test_empty():
    nd = NormalizedDict(normalizer=identity)
    assert dict(nd) == {}
    assert nd.body is None
    assert len(nd) == 0
    assert not bool(nd)

def test_one():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert dict(nd) == {"Foo": "bar"}
    assert nd.body is None
    assert len(nd) == 1
    assert bool(nd)

def test_get_cases():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert nd["Foo"] == "bar"
    assert "foo" not in nd
    assert "FOO" not in nd
    assert "fOO" not in nd

def test_set():
    nd = NormalizedDict(normalizer=identity)
    assert dict(nd) == {}
    nd["Foo"] = "bar"
    assert dict(nd) == {"Foo": "bar"}
    assert len(nd) == 1
    assert nd["Foo"] == "bar"
    nd["fOO"] = "quux"
    assert dict(nd) == {"Foo": "bar", "fOO": "quux"}
    assert len(nd) == 2
    assert nd["Foo"] == "bar"
    assert nd["fOO"] == "quux"

def test_del():
    nd = NormalizedDict({"Foo": "bar", "fOO": "BAR"}, normalizer=identity)
    del nd["Foo"]
    assert dict(nd) == {"fOO": "BAR"}
    del nd["fOO"]
    assert dict(nd) == {}

def test_del_nexists():
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"}, normalizer=identity)
    with pytest.raises(KeyError):
        del nd["fOO"]

def test_eq_empty():
    nd = NormalizedDict(normalizer=identity)
    nd2 = NormalizedDict(normalizer=identity)
    assert nd == nd2

def test_eq_nonempty():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert nd == nd2

def test_neq_cases():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    nd2 = NormalizedDict({"fOO": "bar"}, normalizer=identity)
    assert nd != nd2

def test_neq():
    assert NormalizedDict({"Foo": "bar"}, normalizer=identity) \
        != NormalizedDict({"Foo": "BAR"}, normalizer=identity)

def test_normalized():
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "BAR"}
    assert nd2.body is None
    assert nd == nd2

def test_normalized_with_body():
    nd = NormalizedDict({"Foo": "BAR"}, body='Glarch.', normalizer=identity)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "BAR"}
    assert nd2.body == 'Glarch.'
    assert nd == nd2

def test_normalized_dict():
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    nd2 = nd.normalized_dict()
    assert isinstance(nd2, dict)
    assert nd2 == {"Foo": "BAR"}

def test_eq_dict():
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    assert nd == {"Foo": "BAR"}
    assert {"Foo": "BAR"} == nd
    assert nd != {"FOO": "BAR"}
    assert {"FOO": "BAR"} != nd
    assert nd != {"foo": "BAR"}
    assert {"foo": "BAR"} != nd
    assert nd != {"Foo": "bar"}
    assert {"Foo": "bar"} != nd

def test_body_neq_dict():
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity, body='')
    assert nd != {"Foo": "BAR"}
    assert {"Foo": "BAR"} != nd

def test_eq_body():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity, body='')
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity, body='')
    assert nd == nd2

def test_neq_body():
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity, body='yes')
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity, body='no')
    assert nd != nd2

def test_init_list():
    nd = NormalizedDict([("Foo", "bar"), ("Bar", "baz"), ("FOO", "quux")],
                        normalizer=identity)
    assert dict(nd) == {"Foo": "bar", "FOO": "quux", "Bar": "baz"}
