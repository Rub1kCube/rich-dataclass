from dataclasses import dataclass

from rich_dataclass import JsonConverter, RichDataclassMixin, WrapperConverters


# TODO @demin_vadim: Добавить тесты
# TODO @demin_vadim: Добавить docstring для классов и метод/функций, где это необходимо
# TODO @demin_vadim: Добавить документацию


@dataclass
class Example(RichDataclassMixin):
    bar1: str
    bar2: int

    __converters__ = WrapperConverters(JsonConverter)


example = Example.from_dict({"bar1": "test", "bar2": 1})
print(Example.converters.json.from_obj(data='{"bar1": "cls", "bar2": 42}'))  # noqa: T201
print(Example.converters.json.from_obj(data='{"bar1": "cls", "bar2": 42}'))  # noqa: T201
print(example.converters.json.as_obj())  # noqa: T201
