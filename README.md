# rich-dataclass
A minimalist library for developers who want to avoid writing extra boilerplate.
It provides simple functionality for serializing and deserializing dataclass to dict and json.
This library does not compete with [pydantic](https://github.com/pydantic/pydantic) or [marshmallow](https://github.com/marshmallow-code/marshmallow/), it just offers a lightweight and convenient way to work with dataclass.


## Main Features

### RichDataclassMixin
To add serialization and deserialization functionality to your dataclass, simply inherit from RichDataclassMixin.

#### Mixin methods:
- `from_dict` - creates a dataclass from a dictionary.
- `from_json` - creates a dataclass from JSON. You can pass a string, file path, or file-like object.
- `as_dict` - converts a dataclass to a dictionary.
- `as_json` - converts a dataclass to JSON.

The from_* methods also work with nested dataclasses thanks to [dacite](https://github.com/konradhalas/dacite):
```python
from dataclasses import dataclass
from rich_dataclass import RichDataclassMixin

@dataclass
class NestedOne:
    bar1: str

@dataclass
class NestedTwo:
    bar2: str

@dataclass
class Example(RichDataclassMixin):
    bar3: NestedOne | NestedTwo

example_dataclass = Example.from_dict({"bar3": {"bar2": "example"}})  # Example(bar3=NestedTwo(bar2='example'))
example_dataclass.as_dict()                                           # {'bar3': {'bar2': 'example'}}
```

### Tools
- `rich_dataclass_from_dict_list` — converts a list of dictionaries into a list of dataclass instances inheriting `RichDataclassMixin`. You can pass multiple dataclass types if the dictionaries have different structures.
- `rich_dataclass_to_dict_list`  - converts a list of dataclass instances into a list of dictionaries.
