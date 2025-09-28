import typing as t

from rich_dataclass.converters.abstract import AbstractConverter


class WrapperConverters:
    def __init__(self, *converters: type[AbstractConverter]) -> None:
        self.converters = converters
        self.map_converters = self.__mapping_name_converter(self.converters)

    @staticmethod
    def __mapping_name_converter(
        converters: tuple[type[AbstractConverter], ...],
    ) -> dict[str, type[AbstractConverter]]:
        return {converter.__name_converter__: converter for converter in converters}

    def __getattr__(self, name: str) -> type[AbstractConverter]:
        try:
            return self.map_converters[name]
        except KeyError:
            available = ", ".join(self.map_converters.keys())
            msg = f"Converter '{name}' not found. Available converters: {available}"
            raise AttributeError(msg) from None


class ConverterAdapter:

    def __init__(self, converter: type[AbstractConverter], bound: t.Any) -> None:
        self._converter = converter
        self._bound = bound

    def as_obj(self, **kwargs: t.Any) -> t.Any:
        return self._converter.as_obj(self._bound, **kwargs)

    def from_obj(self, **kwargs: t.Any) -> t.Any:
        return self._converter.from_obj(self._bound, **kwargs)


class ConvertersProxy:

    def __init__(self, wrapper: WrapperConverters, bound: t.Any) -> None:
        self._wrapper = wrapper
        self._bound = bound

    def __getattr__(self, name: str) -> ConverterAdapter:
        converter = getattr(self._wrapper, name)
        return ConverterAdapter(converter, self._bound)
