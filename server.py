'''
Provides a backend to transform the litematic format into a readable one by the frontend
'''

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from litemapy import Schematic

import config
from models.raw_models import RawOutputModel

app = FastAPI()

app.mount('/' + config.TEXTURES_BASE_URL.strip('/'), StaticFiles(directory='static/client_assets/textures'), name='textures')


@app.get('/test-model', response_model=RawOutputModel)
async def test_model():
    schematic = Schematic.load(Path(__file__).parent.joinpath('tests', 'models', 'hole_house_barebones.litematic'))
    result = RawOutputModel.from_schematic(schematic)

    return result
