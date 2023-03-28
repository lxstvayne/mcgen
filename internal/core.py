import typing

import numpy as np
import pydantic
from PIL import Image

from external import pyanvil
from .palette import AbstractPalette, Color

ProgressType = int


class Coordinate(pydantic.BaseModel):
    x: int
    y: int
    z: int

    def __add__(self, other: 'Coordinate') -> 'Coordinate':
        return Coordinate(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: 'Coordinate')  -> 'Coordinate':
        return Coordinate(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def as_tuple(self):
        return self.x, self.y, self.z


Dimension = typing.Union[typing.Literal['xy'], ]


class Frame:
    def __init__(self, data: np.ndarray):
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def width(self):
        return self.data.shape[1]

    @property
    def height(self):
        return self.data.shape[0]

    def preprocess(self) -> np.ndarray:
        return self._resize()

    def _resize(self) -> np.ndarray:
        pass

    @classmethod
    def from_pillow_image(cls, image: Image.Image) -> 'Frame':
        return cls(np.asarray(image))

    def iter_draw_frame(
            self,
            world: pyanvil.World,
            palette: AbstractPalette,
            root_block: Coordinate,
            # dimensions: Dimensions = None,
    ) -> typing.Iterator[ProgressType]:
        with world:
            for h in range(self.height):
                for w in range(self.width):
                    block_pos = root_block + Coordinate(x=w, y=h, z=0)
                    block = world.get_block(block_pos.as_tuple())
                    image_pixel: typing.List[int, int, int] = self.data[h, w]
                    r, g, b = image_pixel
                    block_state = palette.get(Color(r=r, g=g, b=b))
                    block.set_state(block_state)
                    yield h * self.width + w
