from pathlib import Path
import shutil
from zipfile import ZipFile
from argparse import ArgumentParser

'''
Extract the textures from a minecraft client JAR file.
Outputs to the static/textures/ directory
'''

args = ArgumentParser()
args.add_argument('input', type=str)
args = args.parse_args()

base_output_path = Path(__file__).parent.joinpath('static', 'client_assets')

jar_textures_path = 'assets/minecraft/textures/'
jar_blockstates_path = 'assets/minecraft/blockstates/'
jar_models_path = 'assets/minecraft/models/'

def extract_data(zip: ZipFile, jar_prefix: str, output_path: Path):
    for file_name in [fn for fn in zip.namelist() if fn.startswith(jar_prefix)]:
        out_file = file_name[len(jar_prefix):].split('/')
        out_file = output_path.joinpath(*out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        with zip.open(file_name) as source, out_file.open('wb') as out_file:
            shutil.copyfileobj(source, out_file)

with ZipFile(args.input, 'r') as zip:
    extract_data(zip, jar_textures_path, base_output_path.joinpath('textures'))
    extract_data(zip, jar_blockstates_path, base_output_path.joinpath('blockstates'))
    extract_data(zip, jar_models_path, base_output_path.joinpath('models'))
