from typing import Any, Dict, List, Optional, Tuple, Type
import pytest
from headerparser import (
    BodyField,
    BodyNotAllowedError,
    DuplicateFieldError,
    ExtraFields,
    Field,
    MultiExtraFields,
    MultiField,
    UnknownFieldError,
    decode_bool,
    decode_value,
    multidict,
    parsable,
    parse,
)


@parsable
class Simple:
    simple: str
    optional: Optional[str] = None
    aliased: Optional[str] = Field(alias="alias", default=None)
    multi: List[str] = MultiField(factory=list)
    extra: List[Tuple[str, str]] = ExtraFields(factory=list)
    body: Optional[str] = BodyField(default=None)


@parsable
class MultiExtra:
    foo: int = Field(decoder=decode_value(int))
    bar: bool = Field(decoder=decode_bool)
    extra: Dict[str, List[str]] = MultiExtraFields(decoder=multidict, factory=dict)


@parsable
class CrissCross:
    one: str = Field(alias="two")
    two: str = Field(alias="one")


@pytest.mark.parametrize(
    "cls,data,obj",
    [
        (
            Simple,
            "Simple: foobar\n",
            Simple(
                simple="foobar",
                optional=None,
                aliased=None,
                multi=[],
                extra=[],
                body=None,
            ),
        ),
        (
            Simple,
            "Simple: foobar\nOptional: present\nAlias: unknown\nAliased: extra\n"
            "Extra: overflow\nMulti: one\nMulti: two\nHyphen-Ated: Hyphen-Ated\n"
            "\nThis is the body.\n",
            Simple(
                simple="foobar",
                optional="present",
                aliased="unknown",
                multi=["one", "two"],
                extra=[
                    ("aliased", "extra"),
                    ("extra", "overflow"),
                    ("hyphen_ated", "Hyphen-Ated"),
                ],
                body="This is the body.\n",
            ),
        ),
        (
            MultiExtra,
            "Foo: 42\nBar: true\nExtra: one\nExtra: two\nOther: stuff\n",
            MultiExtra(
                foo=42,
                bar=True,
                extra={"extra": ["one", "two"], "other": ["stuff"]},
            ),
        ),
        (MultiExtra, "Bar: no\nFoo: 23\n", MultiExtra(foo=23, bar=False, extra={})),
        (
            CrissCross,
            "ONE: apple\nTWO: banana\n",
            CrissCross(one="banana", two="apple"),
        ),
    ],
)
def test_parse(cls: type, data: str, obj: Any) -> None:
    assert parse(cls, data) == obj


@pytest.mark.parametrize(
    "cls,data,exc_type,exc_match",
    [
        (
            Simple,
            "Simple: one\nSimple: two\n",
            DuplicateFieldError,
            "^Header field 'simple' occurs more than once$",
        ),
        (
            Simple,
            "Simple: foobar\nExtra: one\nExtra: two\n",
            DuplicateFieldError,
            "^Header field 'extra' occurs more than once$",
        ),
        (
            Simple,
            "",
            TypeError,
            "missing 1 required positional argument: 'simple'$",
        ),
        (
            MultiExtra,
            "Foo: forty-two\n",
            ValueError,
            r"^invalid literal for int\(\) with base 10: 'forty-two'$",
        ),
        (MultiExtra, "Bar: maybe\n", ValueError, "invalid boolean: 'maybe'"),
        (
            MultiExtra,
            "Some: field\n\nSome: body\n",
            BodyNotAllowedError,
            "^Message body is present but not allowed$",
        ),
        (
            CrissCross,
            "Unknown: field\n",
            UnknownFieldError,
            "^Unknown header field 'unknown'$",
        ),
    ],
)
def test_parse_error(
    cls: type, data: str, exc_type: Type[Exception], exc_match: str
) -> None:
    with pytest.raises(exc_type, match=exc_match):
        parse(cls, data)
