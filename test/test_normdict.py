from headerparser import NormalizedDict

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


### delitem
### eq with different normalizers
### eq with different bodies
### eq against a normal dict
### different normalizers (identity, hyphens=underscores, titlecase?, etc.)
