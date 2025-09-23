from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, NamedTuple


if TYPE_CHECKING:
    from dataclasses import Field as DataclassField

    from rich_dataclass.types import DataclassInstance


class SerializerReturn(NamedTuple):
    name_field: str
    value_field: Any


class AbstractSerializer(ABC):

    def __init__(self, dataclass: DataclassInstance, field: DataclassField) -> None:
        self.field = field
        self.metadata_field = self.field.metadata
        self.instance_dataclass = dataclass
        self.value_field = getattr(self.instance_dataclass, self.field.name)

    @abstractmethod
    def serializer(self) -> SerializerReturn:
        msg = f"Serializer for field '{self.field.name}' is not implemented in {self.__class__.__name__}"
        raise NotImplementedError(msg)


class AliasSerializer(AbstractSerializer):

    def serializer(self) -> SerializerReturn:
        name_field: str = self.metadata_field.get("alias", self.field.name)
        return SerializerReturn(name_field, self.value_field)
