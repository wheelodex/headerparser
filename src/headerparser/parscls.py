from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from enum import Enum
from functools import partial
import typing as ty
from typing import Any, List, Optional, Tuple, TypeVar, overload
import attr
from .errors import (
    BodyNotAllowedError,
    DuplicateBodyError,
    DuplicateFieldError,
    UnknownFieldError,
)
from .scanner import Scanner
from .types import decode_name

CLS_ATTR_KEY = "__headerparser_spec__"
METADATA_KEY = "headerparser"

T = TypeVar("T")
TT = TypeVar("TT", bound=type)

FieldDecoder = ty.Callable[[str, str], Any]
MultiFieldDecoder = ty.Callable[[str, List[str]], Any]
ExtraFieldsDecoder = ty.Callable[[List[Tuple[str, str]]], Any]
BodyDecoder = ty.Callable[[str], Any]
NameDecoder = ty.Callable[[str], str]


class InKey(Enum):
    EXTRA = "extra"
    BODY = "body"


@attr.define
class BaseFieldProcessor:
    name: str

    @abstractmethod
    def process(self, name: str, value: str) -> None:
        ...

    @abstractmethod
    def finalize(self, data: dict[str, Any]) -> None:
        ...


@attr.define
class FieldProcessor(BaseFieldProcessor):
    name: str
    in_key: str
    decoder: Optional[FieldDecoder]
    state: Optional[str] = None

    def process(self, _: str, value: str) -> None:
        if self.state is None:
            self.state = value
        else:
            raise DuplicateFieldError(self.in_key)

    def finalize(self, data: dict[str, Any]) -> None:
        if self.state is not None:
            value: Any = self.state
            if self.decoder is not None:
                value = self.decoder(self.name, value)
            data[self.name] = value


@attr.define
class MultiFieldProcessor(BaseFieldProcessor):
    name: str
    in_key: str
    decoder: Optional[MultiFieldDecoder]
    state: list[str] = attr.Factory(list)

    def process(self, _: str, value: str) -> None:
        self.state.append(value)

    def finalize(self, data: dict[str, Any]) -> None:
        if self.state:
            value: Any = self.state
            if self.decoder is not None:
                value = self.decoder(self.name, value)
            data[self.name] = value


@attr.define
class ExtraFieldsProcessor(BaseFieldProcessor):
    name: str
    decoder: Optional[ExtraFieldsDecoder]
    state: list[tuple[str, str]] = attr.Factory(list)
    seen: set[str] = attr.Factory(set)

    def process(self, name: str, value: str) -> None:
        if name in self.seen:
            raise DuplicateFieldError(name)
        self.state.append((name, value))
        self.seen.add(name)

    def finalize(self, data: dict[str, Any]) -> None:
        if self.state:
            value: Any = self.state
            if self.decoder is not None:
                value = self.decoder(value)
            data[self.name] = value


@attr.define
class MultiExtraFieldsProcessor(BaseFieldProcessor):
    name: str
    decoder: Optional[ExtraFieldsDecoder]
    state: list[tuple[str, str]] = attr.Factory(list)

    def process(self, name: str, value: str) -> None:
        self.state.append((name, value))

    def finalize(self, data: dict[str, Any]) -> None:
        if self.state:
            value: Any = self.state
            if self.decoder is not None:
                value = self.decoder(value)
            data[self.name] = value


@attr.define
class BodyProcessor(BaseFieldProcessor):
    name: str
    decoder: Optional[BodyDecoder]
    state: Optional[str] = None

    def process(self, _: str, value: str) -> None:
        if self.state is not None:
            raise DuplicateBodyError()
        self.state = value

    def finalize(self, data: dict[str, Any]) -> None:
        if self.state is not None:
            value: Any = self.state
            if self.decoder is not None:
                value = self.decoder(value)
            data[self.name] = value


@attr.define
class BaseFieldSpec(ABC):
    name: str

    @property
    @abstractmethod
    def in_key(self) -> str | InKey:
        ...

    @abstractmethod
    def get_processor(self) -> BaseFieldProcessor:
        ...


@attr.define
class FieldSpec(BaseFieldSpec):
    alias: Optional[str] = None
    decoder: Optional[FieldDecoder] = None

    @property
    def in_key(self) -> str:
        return self.alias if self.alias is not None else self.name

    def get_processor(self) -> BaseFieldProcessor:
        return FieldProcessor(name=self.name, in_key=self.in_key, decoder=self.decoder)


@attr.define
class MultiFieldSpec(BaseFieldSpec):
    alias: Optional[str] = None
    decoder: Optional[MultiFieldDecoder] = None

    @property
    def in_key(self) -> str:
        return self.alias if self.alias is not None else self.name

    def get_processor(self) -> BaseFieldProcessor:
        return MultiFieldProcessor(
            name=self.name, in_key=self.in_key, decoder=self.decoder
        )


@attr.define
class ExtraFieldsSpec(BaseFieldSpec):
    decoder: Optional[ExtraFieldsDecoder] = None

    @property
    def in_key(self) -> InKey:
        return InKey.EXTRA

    def get_processor(self) -> BaseFieldProcessor:
        return ExtraFieldsProcessor(name=self.name, decoder=self.decoder)


class MultiExtraFieldsSpec(ExtraFieldsSpec):
    def get_processor(self) -> BaseFieldProcessor:
        return MultiExtraFieldsProcessor(name=self.name, decoder=self.decoder)


@attr.define
class BodySpec(BaseFieldSpec):
    decoder: Optional[BodyDecoder] = None

    @property
    def in_key(self) -> InKey:
        return InKey.BODY

    def get_processor(self) -> BaseFieldProcessor:
        return BodyProcessor(name=self.name, decoder=self.decoder)


def Field(
    *,
    alias: Optional[str] = None,
    decoder: Optional[FieldDecoder] = None,
    **kwargs: Any,
) -> Any:
    metadata = kwargs.get("metadata")
    if metadata is None:
        metadata = {}
    metadata[METADATA_KEY] = {
        "alias": alias,
        "decoder": decoder,
        "field_type": FieldSpec,
    }
    kwargs["metadata"] = metadata
    return attr.field(**kwargs)


def MultiField(
    *,
    alias: Optional[str] = None,
    decoder: Optional[MultiFieldDecoder] = None,
    **kwargs: Any,
) -> Any:
    metadata = kwargs.get("metadata")
    if metadata is None:
        metadata = {}
    metadata[METADATA_KEY] = {
        "alias": alias,
        "decoder": decoder,
        "field_type": MultiFieldSpec,
    }
    kwargs["metadata"] = metadata
    return attr.field(**kwargs)


def ExtraFields(*, decoder: Optional[ExtraFieldsDecoder] = None, **kwargs: Any) -> Any:
    metadata = kwargs.get("metadata")
    if metadata is None:
        metadata = {}
    metadata[METADATA_KEY] = {"decoder": decoder, "field_type": ExtraFieldsSpec}
    kwargs["metadata"] = metadata
    return attr.field(**kwargs)


def MultiExtraFields(
    *, decoder: Optional[ExtraFieldsDecoder] = None, **kwargs: Any
) -> Any:
    metadata = kwargs.get("metadata")
    if metadata is None:
        metadata = {}
    metadata[METADATA_KEY] = {"decoder": decoder, "field_type": MultiExtraFieldsSpec}
    kwargs["metadata"] = metadata
    return attr.field(**kwargs)


def BodyField(*, decoder: Optional[BodyDecoder] = None, **kwargs: Any) -> Any:
    metadata = kwargs.get("metadata")
    if metadata is None:
        metadata = {}
    metadata[METADATA_KEY] = {"decoder": decoder, "field_type": BodySpec}
    kwargs["metadata"] = metadata
    return attr.field(**kwargs)


def convert_name_decoder(decoder: Optional[NameDecoder]) -> NameDecoder:
    return decoder if decoder is not None else decode_name


def convert_scanner_opts(opts: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    return dict(opts) if opts is not None else {}


@attr.define
class ParsableSpec:
    name_decoder: NameDecoder = attr.field(converter=convert_name_decoder)
    scanner_options: dict[str, Any] = attr.field(converter=convert_scanner_opts)
    fields: dict[str | InKey, BaseFieldSpec]


@overload
def parsable(
    cls: None = None,
    *,
    name_decoder: Optional[NameDecoder] = None,
    scanner_options: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> Callable[[TT], TT]:
    ...


@overload
def parsable(
    cls: TT,
    *,
    name_decoder: Optional[NameDecoder] = None,
    scanner_options: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> TT:
    ...


def parsable(
    cls: Optional[TT] = None,
    *,
    name_decoder: Optional[NameDecoder] = None,
    scanner_options: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> TT | Callable[[TT], TT]:
    if cls is None:
        return partial(  # type: ignore[return-value]
            parsable,
            name_decoder=name_decoder,
            scanner_options=scanner_options,
            **kwargs,
        )
    cls = attr.define(cls, **kwargs)
    fields: dict[str | InKey, BaseFieldSpec] = {}
    for field in attr.fields(cls):
        metadata = (field.metadata or {}).get(METADATA_KEY, {})
        assert isinstance(metadata, dict)
        metadata = metadata.copy()
        ftype = metadata.pop("field_type", FieldSpec)
        assert issubclass(ftype, BaseFieldSpec)
        spec = ftype(name=field.name, **metadata)
        if spec.in_key in fields:
            if isinstance(spec.in_key, str):
                raise ValueError(
                    f"Multiple fields for header name {spec.in_key!r} registered"
                )
            elif spec.in_key is InKey.EXTRA:
                raise ValueError("Multiple extra fields registered")
            elif spec.in_key is InKey.BODY:
                raise ValueError("Multiple body fields registered")
            else:
                raise AssertionError(  # pragma: no cover
                    f"Unhandled InKey {spec.in_key!r}"
                )
        fields[spec.in_key] = spec
    p = ParsableSpec(
        name_decoder=name_decoder,
        scanner_options=scanner_options,
        fields=fields,
    )
    setattr(cls, CLS_ATTR_KEY, p)
    return cls


def parse(cls: type[T], data: str | Iterable[str]) -> T:
    p = getattr(cls, CLS_ATTR_KEY, None)
    if not isinstance(p, ParsableSpec):
        raise TypeError(f"{type(p).__name__} is not a parsable class")
    sc = Scanner(data, **p.scanner_options)
    processors = {k: v.get_processor() for k, v in p.fields.items()}
    for (name, value) in sc.scan():
        if name is not None:
            name = p.name_decoder(name)
            try:
                proc = processors[name]
            except KeyError:
                try:
                    proc = processors[InKey.EXTRA]
                except KeyError:
                    raise UnknownFieldError(name)
        else:
            name = "<BODY>"
            try:
                proc = processors[InKey.BODY]
            except KeyError:
                raise BodyNotAllowedError()
        proc.process(name, value)
    output: dict[str, Any] = {}
    for proc in processors.values():
        proc.finalize(output)
    return cls(**output)  # type: ignore[call-arg]
