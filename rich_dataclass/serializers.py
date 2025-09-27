from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, NamedTuple


if TYPE_CHECKING:
    from dataclasses import Field as DataclassField

    from rich_dataclass.types import DataclassInstance


class FieldSerializerReturn(NamedTuple):
    name_field: str
    value_field: Any


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
