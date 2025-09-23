from __future__ import annotations

from typing import TYPE_CHECKING, Any

import dacite


if TYPE_CHECKING:
    from collections.abc import Sequence

    from rich_dataclass.types import DataclassRichInstance


def rich_dataclass_from_dict_list(
    *serializer_classes: type[DataclassRichInstance],
    items: list[dict[str, Any]],
) -> list[DataclassRichInstance]:
    """Convert a list of dicts into a list of rich dataclass instances."""
    if not serializer_classes:
        msg = "At least one serializer class must be provided."
        raise ValueError(msg)

    result: list[DataclassRichInstance] = []

    for item in items:
        instance = None

        for rich_class in serializer_classes:
            try:
                instance = rich_class.from_dict(item)
                break
            except dacite.DaciteError:
                continue

        if instance is None:
            msg = f"Could not serialize record: {item}"
            raise ValueError(msg)

        result.append(instance)

    return result


def rich_dataclass_to_dict_list(
    instances: Sequence[DataclassRichInstance],
    exclude_none: bool = False,
    exclude: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Convert a list of rich dataclass instances to a list of dictionaries."""
    return [instance.as_dict(exclude_none=exclude_none, exclude=exclude) for instance in instances]
