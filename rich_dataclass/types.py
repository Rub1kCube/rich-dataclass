from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TextIO, Union, runtime_checkable

from typing_extensions import Self, TypeAlias


if TYPE_CHECKING:
    from dataclasses import Field as DataclassField

JsonType: TypeAlias = Union[str, bytes, bytearray, TextIO, Path]


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
    ) -> str: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self: ...

    @classmethod
    def from_json(
        cls,
        data: JsonType,
    ) -> Self: ...
