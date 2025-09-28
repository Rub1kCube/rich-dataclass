import json
from pathlib import Path
from typing import Any, ClassVar, TextIO, TypeAlias

from rich_dataclass.converters.abstract import AbstractConverter
from rich_dataclass.tools import asdict, from_dict
from rich_dataclass.types import DataclassInstance, DataclassRichInstance


JsonType: TypeAlias = str | bytes | bytearray | TextIO | Path


class JsonConverter(AbstractConverter):
    __name_converter__ = "json"

    __json_backend__: ClassVar[Any] = json
    __json_cls_encoder__: ClassVar[Any] = json.JSONEncoder
    __json_cls_decoder__: ClassVar[Any] = json.JSONDecoder

    @classmethod
    def as_obj(  # type: ignore[override]
        cls,
        dataclass_instance: DataclassRichInstance | DataclassInstance,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
        ensure_ascii: bool = False,
    ) -> str:
        """Convert dataclass to JSON string."""
        return cls.__json_backend__.dumps(  # type: ignore[no-any-return]
            asdict(dataclass_instance, exclude_none=exclude_none, exclude=exclude),
            ensure_ascii=ensure_ascii,
            cls=cls.__json_cls_encoder__,
        )

    @classmethod
    def from_obj(  # type: ignore[override]
        cls,
        dataclass: type[DataclassRichInstance | DataclassInstance],
        data: JsonType,
    ) -> DataclassRichInstance | DataclassInstance:
        """Build dataclass from JSON string, auto-parsing nested JSON strings."""
        if isinstance(data, Path):
            data = Path(data).read_text()
        elif hasattr(data, "read"):
            data = data.read()
        parsed = cls.__json_backend__.loads(data, cls=cls.__json_cls_decoder__)
        parsed = cls._parse_nested_json_strings(parsed)
        return from_dict(dataclass, parsed)

    @classmethod
    def _parse_nested_json_strings(cls, obj: Any) -> Any:
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
        if isinstance(obj, dict):
            return {k: cls._parse_nested_json_strings(v) for k, v in obj.items()}
        return obj
