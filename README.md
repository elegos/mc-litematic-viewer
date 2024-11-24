# Minecraft litematic file viewer

The project aims to create a web-based litematic scheme viewer for easy preview.

It's not meant to have a fancy UI or 3d viewer, but a way to get a practical preview of the shape of the schematic.

Future updates might consider adding fancy stuffs, like particles, shaders etc.

## Step 1: extract the textures

As this project doesn't own Mojang's copyrighted material, you'll need to extract the resources from the game's jar file. Use `python ./extract_resources.py` to extract all the required information from the client.