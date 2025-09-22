from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TextIO, runtime_checkable

from typing_extensions import Self


if TYPE_CHECKING:
    from dataclasses import Field as DataclassField
    from pathlib import Path


@runtime_checkable
class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DataclassField[Any]]]


@runtime_checkable
class DataclassRichInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DataclassField[Any]]]

    def as_dict(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]: ...

    def as_json(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
        ensure_ascii: bool = False,
        cls_encoder: type[Any] | None = None,
    ) -> str: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self: ...

    @classmethod
    def from_json(
        cls,
        data: str | bytes | bytearray | Path | TextIO,
        cls_decoder: type[Any] | None = None,
    ) -> Self: ...
