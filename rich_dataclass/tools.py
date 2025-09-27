from __future__ import annotations

from contextlib import suppress
from dataclasses import Field as DataclassField
from dataclasses import asdict
from dataclasses import fields as fields_
from typing import TYPE_CHECKING, Any, overload

from rich_dataclass import RichDataclassMixin
from rich_dataclass.types import DataclassRichInstance

import dacite


if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from rich_dataclass.types import DataclassInstance


def _as_dict(dataclass_instance: DataclassInstance | DataclassRichInstance, **kwargs: Any) -> dict[str, Any]:
    if isinstance(dataclass_instance, DataclassRichInstance):
        return dataclass_instance.as_dict(**kwargs)
    return asdict(dataclass_instance)


def _from_dict(
    dataclass_instance: type[DataclassInstance | DataclassRichInstance],
    data: dict[str, Any],
) -> DataclassInstance | DataclassRichInstance:
    if issubclass(dataclass_instance, RichDataclassMixin):
        return dataclass_instance.from_dict(data=data)
    return dacite.from_dict(dataclass_instance, **data)


def fields(dataclass: DataclassInstance) -> Generator[tuple[DataclassField, Any], None, None]:
    return ((field, getattr(dataclass, field.name)) for field in fields_(dataclass))


@overload
def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: dict[str, Any],
) -> DataclassRichInstance | DataclassInstance: ...


@overload
def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: list[dict[str, Any]],
) -> list[DataclassRichInstance | DataclassInstance]: ...


def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: dict[str, Any] | list[dict[str, Any]],
) -> list[DataclassRichInstance | DataclassInstance] | DataclassRichInstance | DataclassInstance:
    """Convert a list of dicts into a list of rich dataclass instances."""
    if not serializer_classes:
        msg = "At least one serializer class must be provided."
        raise ValueError(msg)

    def dataclass_from_dict(data: dict[str, Any]) -> DataclassRichInstance | DataclassInstance:
        instance = None
        for rich_class in serializer_classes:
            with suppress(Exception):
                instance = _from_dict(rich_class, data)
                break
        if instance is None:
            msg = f"Could not serialize record: {item}"
            raise ValueError(msg)
        return instance

    if isinstance(data, list):
        result: list[DataclassRichInstance | DataclassInstance] = []
        for item in data:
            instance = dataclass_from_dict(item)
            result.append(instance)
        return result
    return dataclass_from_dict(data)


def dataclass_to_dict_list(
    instances: Sequence[DataclassRichInstance | DataclassInstance],
    exclude_none: bool = False,
    exclude: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Convert a list of rich dataclass instances to a list of dictionaries."""
    return [_as_dict(instance, exclude_none=exclude_none, exclude=exclude) for instance in instances]
