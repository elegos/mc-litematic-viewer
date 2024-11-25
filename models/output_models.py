from typing import Optional
from uuid import uuid4

from pydantic.dataclasses import dataclass

from models.raw_models import RawBlock, RawOutputModel, RawSimplifiedBlock, RawSimplifiedBlockNoUV, RawTileEntity


@dataclass
class BlockModel:
    from_coordinate: Optional[tuple[float, float, float]]
    to_coordinate: Optional[tuple[float, float, float]]
    texture: str
    uv: Optional[tuple[int, int, int, int]]
    face: Optional[str]
    positions: list[tuple[int, int, int]]


@dataclass
class OutputRegion:
    textures: dict[str, str]
    blocks: list[BlockModel]

    @staticmethod
    def from_raw_tile_entity(raw_tile_entity: RawTileEntity) -> 'OutputRegion':
        # used for creating the textures index
        inverted_textures: dict[str, str] = {}

        # used to group blocks with the same data but different positions
        unique_block_data: dict[str, BlockModel] = {}

        for block in raw_tile_entity.blocks:
            if isinstance(block, RawSimplifiedBlockNoUV):
                # texture index
                if block.texture not in inverted_textures.keys():
                    inverted_textures[block.texture] = str(uuid4())

                # block grouping
                uv = block.uv if type(block) == RawSimplifiedBlock else None
                simple_dict = {'from': block.from_coordinate, 'to': block.to_coordinate, 'texture': block.texture, 'uv': uv}
                hashed = hash(tuple(sorted(simple_dict.items())))
                if hashed not in unique_block_data.keys():
                    unique_block_data[hashed] = BlockModel(
                        from_coordinate=block.from_coordinate if block.from_coordinate != [0, 0, 0] else None,
                        to_coordinate=block.to_coordinate if block.to_coordinate != [16, 16, 16] else None,
                        texture=inverted_textures[block.texture],
                        uv=uv,
                        face=None,
                        positions=[block.position],
                    )
                else:
                    unique_block_data[hashed].positions.append(block.position)

            elif type(block) == RawBlock:
                # texture index
                for td in block.threed_data:
                    for direction, face in td.faces.items():
                        if face.texture not in inverted_textures.keys():
                            inverted_textures[face.texture] = str(uuid4())

                        simple_dict = {'from': td.from_coordinate, 'to': td.to_coordinate,
                                       'texture': face.texture, 'uv': face.uv, 'face': direction}
                        hashed = hash(tuple(sorted(simple_dict.items())))
                        if hashed not in unique_block_data.keys():
                            unique_block_data[hashed] = BlockModel(
                                from_coordinate=td.from_coordinate if td.from_coordinate != [0, 0, 0] else None,
                                to_coordinate=td.to_coordinate if td.to_coordinate != [16, 16, 16] else None,
                                texture=inverted_textures[face.texture],
                                uv=face.uv,
                                face=direction,
                                positions=[block.position],
                            )
                        else:
                            unique_block_data[hashed].positions.append(block.position)

        return OutputRegion({v: k for k, v in inverted_textures.items()}, list(unique_block_data.values()))


@dataclass
class OutputModel:
    author: str
    name: str
    regions: dict[str, OutputRegion]

    @staticmethod
    def from_raw_model(raw_model: RawOutputModel) -> 'OutputModel':
        return OutputModel(
            author=raw_model.author,
            name=raw_model.name,
            regions={
                reg: OutputRegion.from_raw_tile_entity(raw_model.regions[reg])
                for reg in raw_model.regions
            },
        )
