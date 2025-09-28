from __future__ import annotations

import typing as t
from dataclasses import Field as DataclassField
from dataclasses import fields

from rich_dataclass.converters import ConvertersProxy, WrapperConverters
from rich_dataclass.serializers import AbstractFieldSerializer, FieldSerializerReturn
from rich_dataclass.types import DataclassInstance, DataclassRichInstance

import dacite
from typing_extensions import Self


T = t.TypeVar("T", bound="RichDataclassMixin")


class _ConvertersDescriptor:
    def __get__(self, instance: T | None, owner: type[T]) -> ConvertersProxy:
        if owner.__converters__ is None:
            msg = "No converters registered"
            raise AttributeError(msg)

        bound = instance if instance is not None else owner
        return ConvertersProxy(owner.__converters__, bound)


class RichDataclassMixin:
    """Mixin class for enhancing dataclass functionality."""

    __dacite_config__: t.ClassVar[dacite.Config] = dacite.Config()
    __default_field_serializers__: t.ClassVar[tuple[type[AbstractFieldSerializer]] | None] = None
    __converters__: t.ClassVar[WrapperConverters | None] = None

    converters = _ConvertersDescriptor()

    def _process_field_serializer(self, obj: t.Any, field_: DataclassField) -> FieldSerializerReturn:
        serializers = field_.metadata.get("serializers", [])

        if not isinstance(serializers, list):
            msg = (
                f"Field `{field_.name}` has an invalid value in metadata['serializers']: "
                f"expected an list, got {type(serializers).__name__}"
            )
            raise TypeError(msg)

        if self.__default_field_serializers__:
            serializers.extend(self.__default_field_serializers__)

        name_field = field_.name
        value_field = getattr(obj, field_.name)

        for serializer in serializers:
            if issubclass(serializer, AbstractFieldSerializer):
                serializer_instance = serializer(dataclass_instance=obj, field=field_)
                name_field, value_field = serializer_instance.serializer()

        return FieldSerializerReturn(name_field, value_field)

    def _serialize_value(self, value: DataclassInstance | list | tuple | dict | t.Any) -> t.Any:
        if isinstance(value, (DataclassInstance, DataclassRichInstance)):
            return self._dataclass_to_dict(value)
        if isinstance(value, (list, tuple)):
            return type(value)(self._serialize_value(v) for v in value)
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def _dataclass_to_dict(self, value: DataclassInstance | DataclassRichInstance) -> dict[str, t.Any]:
        return {
            name: self._serialize_value(val)
            for f in fields(value)
            for name, val in [self._process_field_serializer(value, f)]
        }

    def as_dict(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> dict[str, t.Any]:
        """Convert dataclass to dict."""
        data = self._dataclass_to_dict(self)  # type: ignore[arg-type]
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
        return data

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> Self:
        """Build dataclass from dict."""
        return dacite.from_dict(
            data_class=cls,
            data=data,
            config=cls.__dacite_config__,
        )
