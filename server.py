'''
Provides a backend to transform the litematic format into a readable one by the frontend
'''

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from litemapy import Schematic

import config
from models.output_models import OutputModel
from models.raw_models import RawOutputModel

app = FastAPI()

app.mount('/' + config.TEXTURES_BASE_URL.strip('/'), StaticFiles(directory='static/client_assets/textures'), name='textures')


@app.get('/test-model', response_model=OutputModel, response_model_exclude_none=True)
async def test_model():
    schematic = Schematic.load(Path(__file__).parent.joinpath('tests', 'models', 'hole_house_barebones.litematic'))
    raw_result = RawOutputModel.from_schematic(schematic)

    return OutputModel.from_raw_model(raw_result)
