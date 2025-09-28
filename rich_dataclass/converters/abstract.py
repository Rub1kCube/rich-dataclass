import typing as t
from abc import ABC, abstractmethod

from rich_dataclass.types import DataclassInstance, DataclassRichInstance


class AbstractConverter(ABC):
    __name_converter__: t.ClassVar[str]

    @classmethod
    @abstractmethod
    def from_obj(
        cls, dataclass: type[DataclassRichInstance | DataclassInstance], data: t.Any, **kwargs: t.Any
    ) -> DataclassRichInstance | DataclassInstance:
        msg = (
            f"{cls.__name__}.from_obj() must be implemented in a subclass. "
            "It should convert an object into a dataclass instance."
        )
        raise NotImplementedError(msg)

    @classmethod
    @abstractmethod
    def as_obj(
        cls, dataclass_instance: DataclassRichInstance | DataclassInstance, **kwargs: t.Any
    ) -> DataclassRichInstance | DataclassInstance:
        msg = (
            f"{cls.__name__}.as_obj() must be implemented in a subclass. "
            "It should convert a dataclass instance back into the target object."
        )
        raise NotImplementedError(msg)
