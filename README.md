# Minecraft litematic file viewer

The project aims to create a web-based litematic scheme viewer for easy online preview.

It's not meant to have a fancy UI or 3d viewer, but a way to get a practical preview of the shape of the schematic.

Future updates might consider adding fancy stuffs, like particles, shaders etc.

## About the author

Hello, it's me. I'm a former senior developer and currently a manager and software and solution architect. I've always had the interest in videogame programming, though I yet have little vertical background in this field. What I lack the most is the knowledge about rendering in general, so this project aims to shed some light on it.

## State of the art and roadmap

At the moment, the tool is able to render a barebone representation of a demo schematic. It's in pre-whatever stage, so it still needs lots of work, in particular:

- [x] Resources extraction from the client archive (block states, models, textures)
- [x] Litematic file format reading via the `litemapy` module
- [x] Not-so-ugly litematic schematic format conversion in a three.js friendly JSON one
- [x] Barebone representation of the schematic
- [ ] Add support for loading your own schematic (it currently demoes a pre-loaded schematic)
- [ ] Add support to select one or more regions to render (it currently loads them all)
- [ ] Add support for Tile Entities (see ~[models/raw_models.py#L110](models/raw_models.py#L110)), they're currently rendered as single, yellow wool blocks
- [ ] Add support for block state (unsure if the current solution implements it, still navigating at sight)
- [ ] Add support for particles
- [ ] Add support for proper glass panes visualization (currently they appear as ugly sticks!)
- [ ] Add support for better illumination

Any help is appreciated!

## Setup

### Step 1: extract the textures

As this project doesn't own Mojang's copyrighted material, you'll need to extract the resources from the game's jar file. Use `python ./extract_resources.py path/to/the/client.jar` to extract all the required information from the client.

### Step 2: setup the backend's python virtual environment

The virtual environment is based on Pipenv, though a requirements.txt is being made available if you prefere to use whatever venv manager of your choice.

To install the virtual environment with pipenv, just run `pipenv install [-d]` (-d if you want to install the development modules, too, like autopep8).

### Step 3: start the server
To start the server and serve both the backend and the frontend, just run `pipenv run uvicorn server:app` - or use the VS Code "**Serve local web app (debug/reload)**" debug configuration.

## To develop

The IDE / editor of choice is VS Code. For this editor, a set of launch and settings options are being configured in the repository. The "**Resource extractor**" launch option in particular requires the "**Command Variable**" extension in order to select the client's jar file to extract the resources from.
