from dataclasses import dataclass
from functools import reduce
from typing import Literal, Optional, Union

from litemapy import Region, Schematic

from minecraft import get_model_data, get_texture_urls, manage_textures_for_elements


@dataclass
class RawFace3DData:
    uv: tuple[int, int, int, int]
    texture: str
    cullface: Literal[None, 'up', 'down', 'north', 'south', 'west', 'east']

    @staticmethod
    def from_dict(d: dict) -> 'RawFace3DData':
        return RawFace3DData(tuple(d['uv']) if 'uv' in d else None, d['texture'] if 'texture' in d else None, d['cullface'] if 'cullface' in d else None)


@dataclass
class RawBlock3DData:
    from_coordinate: tuple[float, float, float]
    to_coordinate: tuple[float, float, float]
    faces: dict[Literal['up', 'down', 'north', 'south', 'west', 'east', ''], RawFace3DData]

    def with_simplified_faces(self) -> 'RawBlock3DData':
        face_values = [{k: v for k, v in face.__dict__.items() if k != 'cullface'} for k, face in self.faces.items()]

        # Simplified faces (all faces are equal, show only one)
        if reduce(lambda a, b: a if a == b else False, face_values):
            return RawBlock3DData(self.from_coordinate, self.to_coordinate, {'': self.faces[next(k for k in self.faces.keys())]})

        return self


@dataclass
class RawBlock:
    position: tuple[int, int, int]
    threed_data: list[RawBlock3DData]


@dataclass
class RawSimplifiedBlockNoUV:
    position: tuple[int, int, int]
    from_coordinate: tuple[float, float, float]
    to_coordinate: tuple[float, float, float]
    texture: str


@dataclass
class RawSimplifiedBlock(RawSimplifiedBlockNoUV):
    uv: Optional[tuple[int, int, int, int]] = None

    @staticmethod
    def from_block(block: RawBlock) -> Union[RawSimplifiedBlockNoUV, 'RawSimplifiedBlock', RawBlock]:
        # If all faces reference the same Face3DDataOutput but the cullface, use this simplified representation of the object
        # Otherwise use the complex one

        faces = []
        for td in block.threed_data:
            faces.extend([{k: j for k, j in v.__dict__.items() if k != 'cullface'} for k, v in td.faces.items()])
        all_faces_are_equal = True if reduce(lambda a, b: a if a == b else False, faces) else False

        if not all_faces_are_equal:
            return block

        first_face = block.threed_data[0].faces[next((k for k in block.threed_data[0].faces.keys()))]
        if first_face.uv == None:
            return RawSimplifiedBlockNoUV(
                block.position,
                block.threed_data[0].from_coordinate,
                block.threed_data[0].to_coordinate,
                first_face.texture,
            )

        return RawSimplifiedBlock(
            block.position,
            block.threed_data[0].from_coordinate,
            block.threed_data[0].to_coordinate,
            first_face.texture,
            first_face.uv,
        )


@dataclass
class RawTileEntity:
    blocks: list[RawBlock | RawBlock | RawSimplifiedBlock | RawSimplifiedBlockNoUV]

    @staticmethod
    def from_schematic_region(region: Region) -> 'RawTileEntity':
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

                    block_output = RawBlock(
                        (x, y, z),
                        [RawBlock3DData(
                            from_coordinate=tuple(datum['from']),
                            to_coordinate=tuple(datum['to']),
                            faces={
                                key: RawFace3DData.from_dict(value)
                                for key, value in datum['faces'].items()
                            },
                        ).with_simplified_faces() for datum in raw_data_model['elements']]
                    )

                    block_output = RawSimplifiedBlock.from_block(block_output)

                    blocks.append(block_output)

        return RawTileEntity(
            # palette=[PaletteOutput.from_block_state(bs) for bs in region.palette],
            blocks=blocks,
        )


@dataclass
class RawOutputModel:
    author: str
    name: str
    regions: dict[str, RawTileEntity]

    @staticmethod
    def from_schematic(schematic: Schematic) -> 'RawOutputModel':
        return RawOutputModel(
            author=schematic.author,
            name=schematic.name,
            regions={reg: RawTileEntity.from_schematic_region(schematic.regions[reg]) for reg in schematic.regions},
        )
