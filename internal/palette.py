import typing
from abc import ABC, abstractmethod
from json import JSONDecoder, JSONEncoder

import pydantic

from external import pyanvil


class Color(pydantic.BaseModel):
    r: int = pydantic.Field(None, ge=0, le=255)
    g: int = pydantic.Field(None, ge=0, le=255)
    b: int = pydantic.Field(None, ge=0, le=255)

    def __hash__(self):
        return hash((self.r, self.g, self.b))


PaletteType = typing.Dict[Color, pyanvil.BlockState]


class AbstractPalette(ABC):
    def __init__(self, palette: PaletteType):
        self._palette = palette

    def get(self, color: Color) -> pyanvil.BlockState:
        return self.palette.get(color) or self.palette[self.get_nearest(color)]

    @property
    def palette(self):
        return self._palette

    @abstractmethod
    def get_nearest(self, color: Color) -> Color:
        pass

    @classmethod
    def from_file(cls, filename: str) -> 'AbstractPalette':
        with open(filename) as f:
            return cls(palette=PaletteJSONDecoder().decode(f.read()))

    def to_json(self) -> str:
        return PaletteJSONEncoder().default(self)


class Palette(AbstractPalette):
    def get_nearest(self, color: Color) -> Color:
        nearest_color_pair = min(self.palette.items(), key=lambda p: self._delta_formula(color, p[0]))
        nearest_color = nearest_color_pair[0]
        return nearest_color

    @staticmethod
    def _delta_formula(i: Color, j: Color):
        return 30 * (i.r - j.r) ** 2 + 59 * (i.g - j.g) ** 2 + 11 * (i.b - j.b) ** 2


class PaletteJSONEncoder(JSONEncoder):
    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, AbstractPalette):
            return self._encode_palette(o)

        return JSONEncoder.default(self, o)

    @staticmethod
    def _encode_palette(palette: AbstractPalette) -> typing.Any:
        obj = {'colors': []}

        for color, block_state in palette.palette.items():
            obj['colors'].append({'rgb': [color.r, color.g, color.b],
                                  'block_state': {'name': block_state.name, 'props': block_state.props}})

        return JSONEncoder().encode(obj)


class PaletteJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict):
            if 'colors' in obj:
                palette_dict = {
                    Color(r=item["rgb"][0], g=item["rgb"][1], b=item["rgb"][2]): pyanvil.BlockState(
                        item["block_state"]["name"],
                        item["block_state"]["props"])
                    for item in obj['colors']
                }
                return Palette(palette_dict)

        return obj
