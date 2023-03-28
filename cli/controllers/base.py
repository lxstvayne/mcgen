from PIL import Image
from cement import Controller, ex
import rich

from ..core.meta import PackageMetadataInfo

from internal import core, palette
from external import pyanvil

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


package_metadata = PackageMetadataInfo.from_poetry_config_file('pyproject.toml')

VERSION_BANNER = f"""
{package_metadata.name} Does Amazing Things! 
Version: {package_metadata.version}
"""


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = f'{package_metadata.name} Does Amazing Things!'

        # text displayed at the bottom of --help output
        epilog = f'Usage: {package_metadata.name} command1 --foo bar'

        # controller level arguments. ex: 'myapp --version'
        arguments = [
            # add a version banner
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()


class Generate(Controller):
    class Meta:
        label = 'generate'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(help='generate building from image',
        arguments=[
            (
                    [],
                    {'help': 'Input image location',
                     'dest': 'image'}
            ),
            (
                    [],
                    {'help': 'Palette config file',
                     'dest': 'palette'}
            ),
            (
                    [],
                    {'help': 'Map directory',
                     'dest': 'map'}
            ),
            (
                    ['-x'],
                    {'help': 'Root block X coordinate',
                     'dest': 'x'}
            ),
            (
                    ['-y'],
                    {'help': 'Root block Y coordinate',
                     'dest': 'y'}
            ),
            (
                    ['-z'],
                    {'help': 'Root block Z coordinate',
                     'dest': 'z'}
            ),
        ])
    def image(self):
        img = Image.open(self.app.pargs.image)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        p = palette.Palette.from_file(self.app.pargs.palette)
        root_block_coordinate = core.Coordinate(x=self.app.pargs.x, y=self.app.pargs.y, z=self.app.pargs.z)

        frame = core.Frame.from_pillow_image(img)

        console = rich.console.Console()

        progress_bar = Progress(
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console
        )

        blocks_count = frame.height * frame.width

        with progress_bar as progress:
            with pyanvil.World(self.app.pargs.map) as world:
                for _ in zip(progress.track(range(blocks_count)), frame.iter_draw_frame(world, p, root_block_coordinate)):
                    pass

        console.print('Complete!')
