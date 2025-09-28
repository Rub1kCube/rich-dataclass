from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod


if t.TYPE_CHECKING:
    from dataclasses import Field as DataclassField

    from rich_dataclass.types import DataclassInstance


class FieldSerializerReturn(t.NamedTuple):
    name_field: str
    value_field: t.Any


class AbstractFieldSerializer(ABC):
    def __init__(self, dataclass_instance: DataclassInstance, field: DataclassField) -> None:
        self.field = field
        self.metadata_field = self.field.metadata
        self.dataclass_instance = dataclass_instance
        self.value_field = getattr(self.dataclass_instance, self.field.name)

    @abstractmethod
    def serializer(self) -> FieldSerializerReturn:
        msg = f"Serializer for field '{self.field.name}' is not implemented in {self.__class__.__name__}"
        raise NotImplementedError(msg)


class AliasSerializer(AbstractFieldSerializer):
    def serializer(self) -> FieldSerializerReturn:
        name_field: str = self.metadata_field.get("alias", self.field.name)
        return FieldSerializerReturn(name_field, self.value_field)


class AnyTypeToStringSerializer(AbstractFieldSerializer):
    def serializer(self) -> FieldSerializerReturn:
        if not isinstance(self.value_field, str):
            return FieldSerializerReturn(str(self.value_field), self.field.name)
        return FieldSerializerReturn(self.value_field, self.field.name)
