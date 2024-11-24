import json
from pathlib import Path
import random

import config


def _apply_model_data(model_data: dict, result={}):
    for key, val in model_data.items():
        if key in ['parent', 'apply', 'model']:
            continue

        if type(model_data[key]) == dict and key in result:
            result[key] = {**result[key], **model_data[key]}
        else:
            result[key] = val


def _apply_model(model_id: str, result={}):
    stripped_model_id = model_id[len('minecraft:'):] if model_id.startswith('minecraft:') else model_id
    model_path = Path(__file__).parent \
        .joinpath('static', 'client_assets', 'models', f'{stripped_model_id}.json')

    if not model_path.exists():
        raise Exception(f"Model {model_id}'s definition was not found")

    model_data = json.loads(model_path.read_text())

    if 'parent' in model_data:
        _apply_model(model_data['parent'], result)

    _apply_model_data(model_data, result)


def _process_multipart(multipart_data: list[dict], variant_data: dict, result={}):
    for data in multipart_data:
        if 'when' in data:
            for key in data['when']:
                if key in variant_data and data['when'][key] == variant_data[key] and 'apply' in data and 'model' in data['apply']:
                    _apply_model(data['apply']['model'], result)

        elif 'apply' in data:
            if 'model' in data['apply']:
                _apply_model(data['apply']['model'], result)
            _apply_model_data(data['apply'])


def get_model_data(block_id: str, variants: dict[str, str]) -> dict:
    block_state_path = Path(__file__).parent.joinpath('static', 'client_assets',
                                                      'blockstates', f'{block_id[len('minecraft:'):]}.json').resolve()

    if not block_state_path.exists():
        raise Exception(f"Block state {block_id}'s definition was not found")

    result = {}

    raw_data = json.loads(block_state_path.read_text())
    # Multipart handling (chain of responsibility pattern)
    if 'multipart' in raw_data:
        _process_multipart(raw_data['multipart'], variants, result)

    variant_data = None

    if 'variants' in raw_data:
        # Find the corresponding variant
        for variant, n_variant_data in raw_data['variants'].items():
            variant_vals = variant.split(',')
            variant_values: dict[str, str] = {}
            for prop_name, prop_val in [p.split('=') for p in variant_vals if len(p.split('=')) > 1]:
                variant_values[prop_name] = prop_val

            filtered_variants = {key: value for key, value in variants.items() if key in variant_values}

            if variant_values == filtered_variants:
                variant_data = n_variant_data
                break

        if variant_data is None:
            raise Exception(f"Variant {variants} was not found in block state {block_id}")

        # random pick
        if type(variant_data) == list:
            variant_data = random.choice(variant_data)

        if 'model' in variant_data:
            _apply_model(variant_data['model'], result)
        _apply_model_data(variant_data, result)

    return result


def get_texture_urls(texture_data: dict):
    known_keys = [key for key in texture_data.keys() if texture_data[key].startswith('minecraft:')]
    for key in known_keys:
        stripped_texture_id = texture_data[key][len('minecraft:'):] if texture_data[key].startswith('minecraft:') else texture_data[key]
        texture_path = Path(__file__).parent.joinpath('static', 'client_assets', 'textures', f'{stripped_texture_id}.png').resolve()

        if not texture_path.exists():
            raise Exception(f"Texture {texture_data[key]}'s resourse file was not found")

        texture_data[key] = config.TEXTURES_BASE_URL.strip(
            '/') + '/' + str(texture_path.relative_to(Path(__file__).parent.joinpath('static', 'client_assets', 'textures'))).replace('\\', '/')

    keys_with_references = [key for key in texture_data.keys() if texture_data[key].startswith('#')]
    for key in known_keys:
        for ref_key in keys_with_references:
            if texture_data[ref_key] == f'#{key}':
                texture_data[ref_key] = texture_data[key]

    if len([key for key in texture_data.keys() if texture_data[key].startswith('#')]) > 0:
        raise Exception("Not all the referenced textures have been found")


def manage_textures_for_elements(elements: list[dict], textures: dict) -> None:
    for elem in elements:
        if not 'faces' in elem:
            continue

        for face, values in elem['faces'].items():
            if 'texture' in values:
                key = elem['faces'][face]['texture'].lstrip('#')
                if not key in textures.keys():
                    raise Exception(f"Texture {key} was not found in the model's definition")
                elem['faces'][face]['texture'] = textures[key]
