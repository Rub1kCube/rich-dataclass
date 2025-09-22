from __future__ import annotations

import json
from dataclasses import Field as DataclassField
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, ClassVar, TextIO

import dacite
from typing_extensions import Self


class RichDataclassMixin:
    """
    Mixin class for enhancing dataclass functionality.

    This mixin provides methods to convert a dataclass instance to a dictionary
    or JSON string, and to create a dataclass instance from a dictionary or JSON.

    Aliases:
        Fields created with `field(metadata={"alias": "...")` will use the alias name
        instead of the original attribute name when converted with `as_dict` or `as_json`.
    """
    __dacite_config__: ClassVar[dacite.Config] = dacite.Config()
    __json_backend__: ClassVar[Any] = json

    @staticmethod
    def _extract_data_from_field(obj: Any, field_: DataclassField) -> tuple[str, Any]:
        name = field_.name
        value = getattr(obj, name)
        alias = field_.metadata.get("alias")
        name = alias or name
        return name, value

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, RichDataclassMixin):
            return value.as_dict()
        if is_dataclass(value):
            result = {}
            for f in fields(value):
                name, value = self._extract_data_from_field(value, f)
                result[name] = self._serialize_value(value)
            return result
        if isinstance(value, (list, tuple)):
            return type(value)(self._serialize_value(v) for v in value)
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def _asdict(self) -> dict[str, Any]:
        result = {}
        for field_ in fields(self):     # type: ignore[arg-type]
            name, value = self._extract_data_from_field(self, field_)
            result[name] = self._serialize_value(value)
        return result

    def as_dict(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        """Convert dataclass to dict."""
        data = self._asdict()
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        if exclude:
            data = {k: v for k, v in data.items() if v is not exclude}
        return data

    def as_json(
        self,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
        ensure_ascii: bool = False,
        cls_encoder: type[Any] | None = None,
    ) -> str:
        """Convert dataclass to JSON string."""
        return self.__json_backend__.dumps(     # type: ignore[no-any-return]
            self.as_dict(exclude_none=exclude_none, exclude=exclude),
            ensure_ascii=ensure_ascii,
            cls=cls_encoder,
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
        data: str | bytes | bytearray | TextIO | Path,
        cls_decoder: type[Any] | None = None,
    ) -> Self:
        """Build dataclass from JSON string, auto-parsing nested JSON strings."""
        if isinstance(data, Path):
            data = Path(data).read_text()
        elif hasattr(data, "read"):
            data = data.read()
        parsed = cls.__json_backend__.loads(data, cls=cls_decoder)
        parsed = cls._parse_nested_json_strings(parsed)
        return cls.from_dict(parsed)

    @classmethod
    def _parse_nested_json_strings(cls, obj: str | dict[str, Any] | list) -> str | dict[str, Any] | list:
        """Recursively parse strings that look like JSON."""
        if isinstance(obj, str):
            stripped = obj.strip()
            if stripped.startswith(("{", "[")):
                try:
                    return cls._parse_nested_json_strings(json.loads(obj))
                except json.JSONDecodeError:
                    return obj
            return obj
        if isinstance(obj, list):
            return [cls._parse_nested_json_strings(v) for v in obj]
        return {k: cls._parse_nested_json_strings(v) for k, v in obj.items()}
