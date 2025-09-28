from __future__ import annotations

import typing as t

import dacite
from typing_extensions import Self


if t.TYPE_CHECKING:
    from dataclasses import Field as DataclassField

    from rich_dataclass.converters import WrapperConverters
    from rich_dataclass.serializers import AbstractFieldSerializer


@t.runtime_checkable
class DataclassInstance(t.Protocol):
    __dataclass_fields__: t.ClassVar[dict[str, DataclassField[t.Any]]]


@t.runtime_checkable
class DataclassRichInstance(t.Protocol):
    __dataclass_fields__: t.ClassVar[dict[str, DataclassField[t.Any]]]
    __dacite_config__: t.ClassVar[dacite.Config] = dacite.Config()
    __default_field_serializers__: t.ClassVar[tuple[type["AbstractFieldSerializer"]] | None]
    __converters__: t.ClassVar["WrapperConverters" | None]

    converters: "WrapperConverters"

    def as_dict(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> dict[str, t.Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> Self: ...
