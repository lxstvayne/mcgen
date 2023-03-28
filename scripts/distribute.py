import glob
import json
import pathlib
import sys
import typing

import numpy as np
from PIL import Image

from external import pyanvil
from internal.palette import AbstractPalette, PaletteJSONEncoder, Palette, Color


def list_item_in_str(block_list: typing.Iterable[str], block_name: str) -> bool:
    for block_list_name in block_list:
        if block_list_name in block_name:
            return True

    return False


def filter_block_list(block_list: typing.List[str]) -> typing.List[str]:
    """Фильтруем блоки, отбрасывая ступеньки и похожее"""
    # Корни названий блоков
    white_list_words = (
        'wool',
        'bricks',
        'andesite',
        'dirt',
        'planks',
    )

    black_list_words = ('stairs', 'slab', 'command_block', 'item', 'empty', 'stem', 'torch', 'grindstone', 'lamp', 'structure')

    result: typing.List[str] = []

    for block_file in block_list:
        block_name = pathlib.Path(block_file).name
        if list_item_in_str(white_list_words, block_name) \
                and not list_item_in_str(black_list_words, block_name):
            result.append(block_name)

    return result


def get_avg_color_from_image(image_path: str) -> Color:
    img = Image.open(f'{blocks_dir}/{image_path}')
    rgb_im = img.convert('RGB')
    avg_color_per_row = np.average(rgb_im, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    r, g, b, = avg_color
    return Color(r=r, g=g, b=b)


def get_mc_block_name_from_filename(filename: str) -> str:
    return f'minecraft:{filename.split(".")[0]}'


def create_palette(block_list: typing.List[str]) -> Palette:
    palette_dict = {}

    for block_file in block_list:
        palette_dict[get_avg_color_from_image(block_file)] = pyanvil.BlockState(
            get_mc_block_name_from_filename(pathlib.Path(block_file).name), {}
        )

    palette = Palette(palette_dict)

    return palette


def save_result(palette: AbstractPalette, path: str):
    with open(path, 'w+', encoding='utf-8') as out:
        out.write(PaletteJSONEncoder().default(palette))


if __name__ == '__main__':
    blocks_dir = sys.argv[1]
    out_file_path = sys.argv[2]
    block_file_names_with_ext = glob.glob(f'{blocks_dir}/*.png')
    block_file_names_with_ext = filter_block_list(block_file_names_with_ext)
    palette = create_palette(block_file_names_with_ext)
    save_result(palette, out_file_path)
