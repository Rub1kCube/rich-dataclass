from dataclasses import dataclass
from typing import Union

from rich_dataclass import RichDataclassMixin


@dataclass
class Nested:
    field_two: str


@dataclass
class NestedTwo:
    field_three: str


@dataclass
class Example(RichDataclassMixin):
    field_one: Union[Nested, NestedTwo]


example_dataclass = Example.from_dict({"field_one": {"field_three": "example"}})
print(example_dataclass.as_dict())