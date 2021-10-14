import pytest
from headerparser import NormalizedDict


def identity(s: str) -> str:
    return s


def test_empty() -> None:
    nd = NormalizedDict(normalizer=identity)
    assert dict(nd) == {}
    assert nd.body is None
    assert len(nd) == 0
    assert not bool(nd)
    assert nd.normalizer is identity


def test_one() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert dict(nd) == {"Foo": "bar"}
    assert nd.body is None
    assert len(nd) == 1
    assert bool(nd)
    assert nd.normalizer is identity


def test_get_cases() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert nd["Foo"] == "bar"
    assert "foo" not in nd
    assert "FOO" not in nd
    assert "fOO" not in nd


def test_set() -> None:
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


def test_del() -> None:
    nd = NormalizedDict({"Foo": "bar", "fOO": "BAR"}, normalizer=identity)
    del nd["Foo"]
    assert dict(nd) == {"fOO": "BAR"}
    del nd["fOO"]
    assert dict(nd) == {}


def test_del_nexists() -> None:
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"}, normalizer=identity)
    with pytest.raises(KeyError):
        del nd["fOO"]


def test_eq_empty() -> None:
    nd = NormalizedDict(normalizer=identity)
    nd2 = NormalizedDict(normalizer=identity)
    assert nd == nd2


def test_eq_nonempty() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    assert nd == nd2


def test_neq_cases() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    nd2 = NormalizedDict({"fOO": "bar"}, normalizer=identity)
    assert nd != nd2


def test_neq() -> None:
    assert NormalizedDict({"Foo": "bar"}, normalizer=identity) != NormalizedDict(
        {"Foo": "BAR"}, normalizer=identity
    )


def test_normalized() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "BAR"}
    assert nd2.body is None
    assert nd2.normalizer is identity
    assert nd == nd2


def test_normalized_with_body() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, body="Glarch.", normalizer=identity)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "BAR"}
    assert nd2.body == "Glarch."
    assert nd2.normalizer is identity
    assert nd == nd2


def test_normalized_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    nd2 = nd.normalized_dict()
    assert isinstance(nd2, dict)
    assert nd2 == {"Foo": "BAR"}


def test_eq_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity)
    assert nd == {"Foo": "BAR"}
    assert {"Foo": "BAR"} == nd
    assert nd != {"FOO": "BAR"}
    assert {"FOO": "BAR"} != nd
    assert nd != {"foo": "BAR"}
    assert {"foo": "BAR"} != nd
    assert nd != {"Foo": "bar"}
    assert {"Foo": "bar"} != nd


def test_body_neq_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, normalizer=identity, body="")
    assert nd != {"Foo": "BAR"}
    assert {"Foo": "BAR"} != nd


def test_eq_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity, body="")
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity, body="")
    assert nd == nd2


def test_neq_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity, body="yes")
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=identity, body="no")
    assert nd != nd2


def test_init_list() -> None:
    nd = NormalizedDict(
        [("Foo", "bar"), ("Bar", "baz"), ("FOO", "quux")], normalizer=identity
    )
    assert dict(nd) == {"Foo": "bar", "FOO": "quux", "Bar": "baz"}


def test_copy() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=identity)
    nd2 = nd.copy()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "bar"}
    assert nd2.body is None
    assert nd2.normalizer is identity
    assert nd == nd2
    nd2["Foo"] = "gnusto"
    assert dict(nd) == {"Foo": "bar"}
    assert dict(nd2) == {"Foo": "gnusto"}
    assert nd != nd2
    nd2["fOO"] = "quux"
    assert dict(nd) == {"Foo": "bar"}
    assert dict(nd2) == {"Foo": "gnusto", "fOO": "quux"}
    assert nd != nd2


def test_copy_with_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, body="Glarch.", normalizer=identity)
    nd2 = nd.copy()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "bar"}
    assert nd2.body == "Glarch."
    assert nd2.normalizer is identity
    assert nd == nd2
    nd2.body = "quux"
    assert nd.body == "Glarch."
    assert nd2.body == "quux"
    assert nd != nd2
