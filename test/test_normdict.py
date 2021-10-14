import re
from typing import Callable, Dict, Optional
import pytest
from headerparser import NormalizedDict, lower


def test_empty() -> None:
    nd = NormalizedDict()
    assert dict(nd) == {}
    assert nd.body is None
    assert len(nd) == 0
    assert not bool(nd)
    assert nd.normalizer is lower


def test_one() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    assert dict(nd) == {"Foo": "bar"}
    assert nd.body is None
    assert len(nd) == 1
    assert bool(nd)
    assert nd.normalizer is lower


def test_get_cases() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    assert nd["Foo"] == "bar"
    assert nd["Foo"] == nd["foo"] == nd["FOO"] == nd["fOO"]


def test_set() -> None:
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


def test_del() -> None:
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"})
    del nd["Foo"]
    assert dict(nd) == {"Bar": "FOO"}
    del nd["BAR"]
    assert dict(nd) == {}


def test_del_nexists() -> None:
    nd = NormalizedDict({"Foo": "bar", "Bar": "FOO"})
    with pytest.raises(KeyError):
        del nd["Baz"]


def test_eq_empty() -> None:
    nd = NormalizedDict()
    nd2 = NormalizedDict()
    assert nd == nd2


def test_eq_nonempty() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    nd2 = NormalizedDict({"Foo": "bar"})
    assert nd == nd2


def test_eq_cases() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    nd2 = NormalizedDict({"fOO": "bar"})
    assert nd == nd2


def test_neq() -> None:
    assert NormalizedDict({"Foo": "bar"}) != NormalizedDict({"Foo": "BAR"})


def test_normalized() -> None:
    nd = NormalizedDict({"Foo": "BAR"})
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"foo": "BAR"}
    assert nd2.body is None
    assert nd == nd2


def test_normalized_with_body() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, body="Glarch.")
    nd2 = nd.normalized()
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"foo": "BAR"}
    assert nd2.body == "Glarch."
    assert nd == nd2


def test_normalized_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"})
    nd2 = nd.normalized_dict()
    assert isinstance(nd2, dict)
    assert nd2 == {"foo": "BAR"}


def test_eq_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"})
    assert nd == {"Foo": "BAR"}
    assert {"Foo": "BAR"} == nd
    assert nd == {"FOO": "BAR"}
    assert {"FOO": "BAR"} == nd
    assert nd == {"foo": "BAR"}
    assert {"foo": "BAR"} == nd
    assert nd != {"Foo": "bar"}
    assert {"Foo": "bar"} != nd


def test_body_neq_dict() -> None:
    nd = NormalizedDict({"Foo": "BAR"}, body="")
    assert nd != {"Foo": "BAR"}
    assert {"Foo": "BAR"} != nd


def test_eq_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, body="")
    nd2 = NormalizedDict({"fOO": "bar"}, body="")
    assert nd == nd2


def test_neq_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, body="yes")
    nd2 = NormalizedDict({"fOO": "bar"}, body="no")
    assert nd != nd2


def test_neq_none() -> None:
    assert NormalizedDict() != None  # noqa: E711
    assert None != NormalizedDict()  # noqa: E711


def test_neq_bool() -> None:
    assert NormalizedDict() != False  # noqa: E712
    assert False != NormalizedDict()  # noqa: E712


def test_neq_int() -> None:
    assert NormalizedDict() != 42
    assert 42 != NormalizedDict()


def test_init_list() -> None:
    nd = NormalizedDict([("Foo", "bar"), ("Bar", "baz"), ("FOO", "quux")])
    assert dict(nd) == {"FOO": "quux", "Bar": "baz"}


def test_copy() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    nd2 = nd.copy()
    assert nd is not nd2
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "bar"}
    assert nd2.body is None
    assert nd == nd2
    nd2["Foo"] = "gnusto"
    assert dict(nd) == {"Foo": "bar"}
    assert dict(nd2) == {"Foo": "gnusto"}
    assert nd != nd2
    nd2["fOO"] = "quux"
    assert dict(nd) == {"Foo": "bar"}
    assert dict(nd2) == {"fOO": "quux"}
    assert nd != nd2
    nd2["Glarch"] = "baz"
    assert dict(nd) == {"Foo": "bar"}
    assert dict(nd2) == {"fOO": "quux", "Glarch": "baz"}
    assert nd != nd2


def test_copy_with_body() -> None:
    nd = NormalizedDict({"Foo": "bar"}, body="Glarch.")
    nd2 = nd.copy()
    assert nd is not nd2
    assert isinstance(nd2, NormalizedDict)
    assert dict(nd2) == {"Foo": "bar"}
    assert nd2.body == "Glarch."
    assert nd == nd2
    nd2.body = "quux"
    assert nd.body == "Glarch."
    assert nd2.body == "quux"
    assert nd != nd2


def test_neq_normalizers_empty() -> None:
    nd = NormalizedDict()
    nd2 = NormalizedDict(normalizer=lambda x: x)
    assert dict(nd) == dict(nd2) == {}
    assert nd != nd2


def test_neq_normalizers_nonempty() -> None:
    nd = NormalizedDict({"Foo": "bar"})
    nd2 = NormalizedDict({"Foo": "bar"}, normalizer=lambda x: x)
    assert dict(nd) == dict(nd2) == {"Foo": "bar"}
    assert nd != nd2


def normdash(s: str) -> str:
    return re.sub(r"[-_\s]+", "-", s.lower())


def identity(s: str) -> str:
    return s


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"Foo": "Bar"},
        {"foo": "Bar"},
        {"FOO_BAR": "BAZ"},
    ],
)
@pytest.mark.parametrize("normalizer", [None, lower, normdash, identity])
@pytest.mark.parametrize("body", [None, "Glarch."])
def test_repr(
    data: Dict[str, str],
    normalizer: Optional[Callable[[str], str]],
    body: Optional[str],
) -> None:
    nd = NormalizedDict(data, body=body, normalizer=normalizer)
    assert repr(nd) == (
        f"headerparser.normdict.NormalizedDict({data!r},"
        f" normalizer={normalizer!r}, body={body!r})"
    )
