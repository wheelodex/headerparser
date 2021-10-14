import re
import pytest
from headerparser import NormalizedDict


def normdash(s: str) -> str:
    return re.sub(r"[-_\s]+", "-", s.lower())


def test_empty() -> None:
    nd = NormalizedDict(normalizer=normdash)
    assert dict(nd) == {}
    assert nd.body is None
    assert len(nd) == 0
    assert not bool(nd)
    assert nd.normalizer is normdash


def test_one() -> None:
    nd = NormalizedDict({"A Key": "bar"}, normalizer=normdash)
    assert dict(nd) == {"A Key": "bar"}
    assert nd.body is None
    assert len(nd) == 1
    assert bool(nd)
    assert nd.normalizer is normdash


def test_get_cases() -> None:
    nd = NormalizedDict({"A Key": "bar"}, normalizer=normdash)
    assert nd["A Key"] == "bar"
    assert nd["A Key"] == nd["a_key"] == nd["A-KEY"] == nd["A - key"]


def test_set() -> None:
    nd = NormalizedDict(normalizer=normdash)
    assert dict(nd) == {}
    nd["A Key"] = "bar"
    assert dict(nd) == {"A Key": "bar"}
    assert nd["A Key"] == "bar"
    assert nd["A Key"] == nd["a_key"] == nd["A-KEY"] == nd["A - key"]
    nd["A-Key"] = "quux"
    assert dict(nd) == {"A-Key": "quux"}
    assert nd["A Key"] == "quux"
    assert nd["A Key"] == nd["a_key"] == nd["A-KEY"] == nd["A - key"]


def test_del() -> None:
    nd = NormalizedDict(
        {"A Key": "bar", "Another-Key": "FOO"},
        normalizer=normdash,
    )
    del nd["A Key"]
    assert dict(nd) == {"Another-Key": "FOO"}
    del nd["ANOTHER_KEY"]
    assert dict(nd) == {}


def test_del_nexists() -> None:
    nd = NormalizedDict(
        {"A Key": "bar", "Another-Key": "FOO"},
        normalizer=normdash,
    )
    with pytest.raises(KeyError):
        del nd["AKey"]


def test_eq_empty() -> None:
    nd = NormalizedDict(normalizer=normdash)
    nd2 = NormalizedDict(normalizer=normdash)
    assert nd == nd2


def test_eq_nonempty() -> None:
    nd = NormalizedDict({"Foo": "bar"}, normalizer=normdash)
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=normdash)
    assert nd == nd2


def test_eq_cases() -> None:
    nd = NormalizedDict({"A Key": "bar"}, normalizer=normdash)
    nd2 = NormalizedDict({"a_key": "bar"}, normalizer=normdash)
    assert nd == nd2


def test_neq() -> None:
    assert NormalizedDict({"A Key": "A Value"}, normalizer=normdash) != NormalizedDict(
        {"A Key": "a_value"}, normalizer=normdash
    )


def test_normalized() -> None:
    nd = NormalizedDict({"A Key": "BAR"}, normalizer=normdash)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"a-key": "BAR"}
    assert nd2.body is None
    assert nd2.normalizer is normdash
    assert nd == nd2


def test_normalized_with_body() -> None:
    nd = NormalizedDict({"A Key": "BAR"}, body="Foo Baz", normalizer=normdash)
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"a-key": "BAR"}
    assert nd2.body == "Foo Baz"
    assert nd2.normalizer is normdash
    assert nd == nd2


def test_normalized_dict() -> None:
    nd = NormalizedDict({"A Key": "BAR"}, normalizer=normdash)
    nd2 = nd.normalized_dict()
    assert isinstance(nd2, dict)
    assert nd2 == {"a-key": "BAR"}


def test_eq_dict() -> None:
    nd = NormalizedDict({"A Key": "BAR"}, normalizer=normdash)
    assert nd == {"A Key": "BAR"}
    assert {"A Key": "BAR"} == nd
    assert nd == {"A_KEY": "BAR"}
    assert {"A_KEY": "BAR"} == nd
    assert nd == {"a-key": "BAR"}
    assert {"a-key": "BAR"} == nd
    assert nd != {"A Key": "bar"}
    assert {"A Key": "bar"} != nd


def test_body_neq_dict() -> None:
    nd = NormalizedDict({"A Key": "BAR"}, body="", normalizer=normdash)
    assert nd != {"A Key": "BAR"}
    assert {"A Key": "BAR"} != nd


def test_eq_body() -> None:
    nd = NormalizedDict({"A Key": "bar"}, body="", normalizer=normdash)
    nd2 = NormalizedDict({"a_KEY": "bar"}, body="", normalizer=normdash)
    assert nd == nd2


def test_neq_body() -> None:
    nd = NormalizedDict({"A Key": "bar"}, body="yes", normalizer=normdash)
    nd2 = NormalizedDict({"a_KEY": "bar"}, body="no", normalizer=normdash)
    assert nd != nd2


def test_init_list() -> None:
    nd = NormalizedDict(
        [("A Key", "bar"), ("Another-Key", "baz"), ("A_KEY", "quux")],
        normalizer=normdash,
    )
    assert dict(nd) == {"A_KEY": "quux", "Another-Key": "baz"}


def test_copy() -> None:
    nd = NormalizedDict({"A Key": "bar"}, normalizer=normdash)
    nd2 = nd.copy()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"A Key": "bar"}
    assert nd2.body is None
    assert nd2.normalizer is normdash
    assert nd == nd2
    nd2["A Key"] = "gnusto"
    assert dict(nd) == {"A Key": "bar"}
    assert dict(nd2) == {"A Key": "gnusto"}
    assert nd != nd2
    nd2["a-key"] = "quux"
    assert dict(nd) == {"A Key": "bar"}
    assert dict(nd2) == {"a-key": "quux"}
    assert nd != nd2
    nd2["Another_Key"] = "baz"
    assert dict(nd) == {"A Key": "bar"}
    assert dict(nd2) == {"a-key": "quux", "Another_Key": "baz"}
    assert nd != nd2


def test_copy_with_body() -> None:
    nd = NormalizedDict({"A Key": "bar"}, body="Glarch.", normalizer=normdash)
    nd2 = nd.copy()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"A Key": "bar"}
    assert nd2.body == "Glarch."
    assert nd2.normalizer is normdash
    assert nd == nd2
    nd2.body = "quux"
    assert nd.body == "Glarch."
    assert nd2.body == "quux"
    assert nd != nd2
