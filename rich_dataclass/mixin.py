from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import Field as DataclassField
from dataclasses import fields
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import dacite
from typing_extensions import Self

from rich_dataclass.serializers import AbstractSerializer, SerializerReturn
from rich_dataclass.types import DataclassInstance, DataclassRichInstance


if TYPE_CHECKING:
    from rich_dataclass.types import JsonType


class RichDataclassMixin:
    """
    Mixin class for enhancing dataclass functionality.

    This mixin provides methods to convert a dataclass instance to a dictionary
    or JSON string, and to create a dataclass instance from a dictionary or JSON.
    """

    __dacite_config__: ClassVar[dacite.Config] = dacite.Config()

    __json_backend__: ClassVar[Any] = json
    __json_cls_encoder__: ClassVar[Any] = json.JSONEncoder
    __json_cls_decoder__: ClassVar[Any] = json.JSONDecoder

    @staticmethod
    def _process_field_serializer(obj: Any, field_: DataclassField) -> SerializerReturn:
        serializers = field_.metadata.get("serializers", [])
        name_field = field_.name
        value_field = getattr(obj, field_.name)

        if not isinstance(serializers, Iterable):
            msg = ""
            raise TypeError(msg)

        for serializer in serializers:
            if issubclass(serializer, AbstractSerializer):
                serializer_instance = serializer(dataclass=obj, field=field_)
                name_field, value_field = serializer_instance.serializer()

        return SerializerReturn(name_field, value_field)

    def _serialize_value(self, value: DataclassInstance | list | tuple | dict | Any) -> Any:
        if isinstance(value, (DataclassInstance, DataclassRichInstance)):
            return self._dataclass_to_dict(value)
        if isinstance(value, (list, tuple)):
            return type(value)(self._serialize_value(v) for v in value)
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def _dataclass_to_dict(self, value: DataclassInstance | DataclassRichInstance) -> dict[str, Any]:
        return {
            name: self._serialize_value(val)
            for f in fields(value)
            for name, val in [self._process_field_serializer(value, f)]
        }

    def as_dict(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        """Convert dataclass to dict."""
        data = self._dataclass_to_dict(self)  # type: ignore[arg-type]
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
        return data

    def as_json(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
        ensure_ascii: bool = False,
    ) -> str:
        """Convert dataclass to JSON string."""
        return self.__json_backend__.dumps(  # type: ignore[no-any-return]
            self.as_dict(exclude_none=exclude_none, exclude=exclude),
            ensure_ascii=ensure_ascii,
            cls=self.__json_cls_encoder__,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build dataclass from dict."""
        return dacite.from_dict(
            data_class=cls,
            data=data,
            config=cls.__dacite_config__,
        )

    @classmethod
    def from_json(
        cls,
        data: JsonType,
    ) -> Self:
        """Build dataclass from JSON string, auto-parsing nested JSON strings."""
        if isinstance(data, Path):
            data = Path(data).read_text()
        elif hasattr(data, "read"):
            data = data.read()
        parsed = cls.__json_backend__.loads(data, cls=cls.__json_cls_decoder__)
        parsed = cls._parse_nested_json_strings(parsed)
        return cls.from_dict(parsed)

    @classmethod
    def _parse_nested_json_strings(cls, obj: str | dict[str, Any] | list) -> str | dict[str, Any] | list:
        """Recursively parse strings that look like JSON."""
        if isinstance(obj, str):
            stripped = obj.strip()
            if stripped.startswith(("{", "[")):
                try:
                    return cls._parse_nested_json_strings(cls.__json_backend__.loads(obj))
                except Exception:  # noqa: BLE001
                    return obj
            return obj
        if isinstance(obj, list):
            return [cls._parse_nested_json_strings(v) for v in obj]
        return {k: cls._parse_nested_json_strings(v) for k, v in obj.items()}
