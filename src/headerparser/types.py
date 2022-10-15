from __future__ import annotations
from collections.abc import Callable, Iterable
import re
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

TRUTHY = {"yes", "y", "on", "true", "1"}
FALSEY = {"no", "n", "off", "false", "0"}


def BOOL(s: str) -> bool:
    """
    Convert boolean-like strings to `bool` values.  The strings ``'yes'``,
    ``'y'``, ``'on'``, ``'true'``, and ``'1'`` are converted to `True`, and the
    strings ``'no'``, ``'n'``, ``'off'``, ``'false'``, and ``'0'`` are
    converted to `False`.  The conversion is case-insensitive and ignores
    leading & trailing whitespace.  Any value that cannot be converted to a
    `bool` results in a `ValueError`.

    :param string s: a boolean-like string to convert to a `bool`
    :rtype: bool
    :raises ValueError: if ``s`` is not one of the values listed above
    """
    b = s.strip().lower()
    if b in TRUTHY:
        return True
    elif b in FALSEY:
        return False
    else:
        raise ValueError(f"invalid boolean: {s!r}")


def lower(s: Any) -> Any:
    """
    .. versionadded:: 0.2.0

    Convert ``s`` to lowercase by calling its :meth:`~str.lower()` method if it
    has one; otherwise, return ``s`` unchanged
    """
    try:
        return s.lower()
    except (TypeError, AttributeError):
        return s


def unfold(s: str) -> str:
    r"""
    .. versionadded:: 0.2.0

    Remove folding whitespace from a string by converting line breaks (and any
    whitespace adjacent to line breaks) to a single space and removing leading
    & trailing whitespace.

    >>> unfold('This is a \n folded string.\n')
    'This is a folded string.'

    :param string s: a string to unfold
    :rtype: string
    """
    return re.sub(r"[ \t]*[\r\n][ \t\r\n]*", " ", s).strip(" ")


def decode_bool(_: str, value: str) -> bool:
    return BOOL(value)


def decode_value(func: Callable[[str], T]) -> Callable[[str, str], T]:
    def decoder(_: str, value: str) -> T:
        return func(value)

    return decoder


def multidict(values: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    data: dict[K, list[V]] = {}
    for k, v in values:
        data.setdefault(k, []).append(v)
    return data


def decode_name(name: str) -> str:
    return re.sub(r"\W", "_", name.lower())
