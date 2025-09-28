from __future__ import annotations

import typing as t
from contextlib import suppress
from dataclasses import Field as DataclassField
from dataclasses import asdict as asdict_dataclass
from dataclasses import fields as fields_

import dacite


if t.TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from typing import TypeGuard

    from rich_dataclass.types import DataclassInstance, DataclassRichInstance


def is_rich_dataclass(annotations: t.Any) -> "TypeGuard[type[DataclassRichInstance]]":
    return (
        hasattr(annotations, "__dataclass_fields__")
        and hasattr(annotations, "__dacite_config__")
        and hasattr(annotations, "__default_field_serializers__")
        and hasattr(annotations, "__converters__")
    )


def asdict(dataclass_instance: DataclassInstance | DataclassRichInstance, **kwargs: t.Any) -> dict[str, t.Any]:
    if is_rich_dataclass(dataclass_instance):
        return dataclass_instance.as_dict(**kwargs)
    return asdict_dataclass(dataclass_instance)


def from_dict(
    dataclass: type[DataclassInstance | DataclassRichInstance],
    data: dict[str, t.Any],
) -> DataclassInstance | DataclassRichInstance:
    if is_rich_dataclass(dataclass):
        return dataclass.from_dict(data=data)
    return dacite.from_dict(dataclass, **data)


def fields(dataclass: DataclassInstance) -> Generator[tuple[DataclassField, t.Any], None, None]:
    return ((field, getattr(dataclass, field.name)) for field in fields_(dataclass))


@t.overload
def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: dict[str, t.Any],
) -> DataclassRichInstance | DataclassInstance: ...


@t.overload
def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: list[dict[str, t.Any]],
) -> list[DataclassRichInstance | DataclassInstance]: ...


def dataclass_from_dict(
    *serializer_classes: type[DataclassRichInstance | DataclassInstance],
    data: dict[str, t.Any] | list[dict[str, t.Any]],
) -> list[DataclassRichInstance | DataclassInstance] | DataclassRichInstance | DataclassInstance:
    """Convert a list of dicts into a list of rich dataclass instances."""
    if not serializer_classes:
        msg = "At least one serializer class must be provided."
        raise ValueError(msg)

    def dataclass_from_dict(data: dict[str, t.Any]) -> DataclassRichInstance | DataclassInstance:
        instance = None
        for dataclass_class in serializer_classes:
            with suppress(Exception):
                instance = from_dict(dataclass_class, data)
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
) -> list[dict[str, t.Any]]:
    """Convert a list of rich dataclass instances to a list of dictionaries."""
    return [asdict(instance, exclude_none=exclude_none, exclude=exclude) for instance in instances]


def dataclass_to_convert_obj_list(
    instances: Sequence[DataclassRichInstance | DataclassInstance],
    converter_name: str,
    **kwargs: t.Any,
) -> list[t.Any]:
    return [getattr(instance, converter_name).as_obj(**kwargs) for instance in instances]
