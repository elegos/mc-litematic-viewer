from dataclasses import dataclass
from typing import Literal

from litemapy import Region, Schematic

from minecraft import get_model_data, get_texture_urls, manage_textures_for_elements


@dataclass
class Face3DDataOutput:
    uv: tuple[int, int, int, int]
    texture: str
    cullface: Literal[None, 'up', 'down', 'north', 'south', 'west', 'east']

    @staticmethod
    def from_dict(d: dict) -> 'Face3DDataOutput':
        return Face3DDataOutput(tuple(d['uv']) if 'uv' in d else None, d['texture'] if 'texture' in d else None, d['cullface'] if 'cullface' in d else None)


@dataclass
class Block3DDataOutput:
    from_coordinate: tuple[float, float, float]
    to_coordinate: tuple[float, float, float]
    faces: dict[Literal['up', 'down', 'north', 'south', 'west', 'east'], Face3DDataOutput]


@dataclass
class BlockOutput:
    position: tuple[int, int, int]
    threed_data: list[Block3DDataOutput]


@dataclass
class TileEntityOutput:
    blocks: list[BlockOutput]

    @staticmethod
    def from_schematic_region(region: Region) -> 'TileEntityOutput':
        blocks = []
        for x in region.range_x():
            for y in region.range_y():
                for z in region.range_z():
                    block = region[x, y, z]

                    if block.id == 'minecraft:air':
                        continue

                    raw_data_model = get_model_data(block.id, block._BlockState__properties)

                    if 'elements' not in raw_data_model:
                        # search within the tile entities
                        tile_entity = next((te for te in region.tile_entities if str(te.data['id']) == block.id), None)

                        if tile_entity is None:
                            raise Exception(f"Tile entity {block.id} was not found in the schematic")

                        # TODO: find the solution to recreate the elements somehow.
                        # For now, default to an arbitrary element (yellow wool block)
                        raw_data_model['elements'] = [{
                            'from': (0, 0, 0),
                            'to': (16, 16, 16),
                            'faces': {
                                'down': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'down'},
                                'up': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'up'},
                                'north': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'north'},
                                'south': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'south'},
                                'west': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'west'},
                                'east': {'uv': (16, 0, 0, 16), 'texture': '#all', 'cullface': 'east'}
                            }
                        }]
                        raw_data_model['textures'] = {'all': 'minecraft:block/yellow_wool'}

                    if 'textures' in raw_data_model:
                        get_texture_urls(raw_data_model['textures'])
                    manage_textures_for_elements(raw_data_model['elements'], raw_data_model['textures'])

                    blocks.append(BlockOutput(
                        (x, y, z),
                        [Block3DDataOutput(
                            from_coordinate=tuple(datum['from']),
                            to_coordinate=tuple(datum['to']),
                            faces={
                                key: Face3DDataOutput.from_dict(value)
                                for key, value in datum['faces'].items()
                            },
                        ) for datum in raw_data_model['elements']]
                    ))

        return TileEntityOutput(
            # palette=[PaletteOutput.from_block_state(bs) for bs in region.palette],
            blocks=blocks,
        )


@dataclass
class OutputModel:
    author: str
    regions: dict[str, TileEntityOutput]

    @staticmethod
    def from_schematic(schematic: Schematic) -> 'OutputModel':
        return OutputModel(
            author=schematic.author,
            regions={reg: TileEntityOutput.from_schematic_region(schematic.regions[reg]) for reg in schematic.regions},
        )
