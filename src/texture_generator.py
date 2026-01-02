import json
import os
import random
from PIL import Image

# Local imports
from src.data.leafblock import LeafBlock
from src.texturepack_utils import scanPacksForTexture
from src.utilities import list_files_alphabetically, printOverride

def generateTexture(leaf: LeafBlock, root, infile, useProgrammerArt=False):
    outfolder = root.replace("assets", "").replace("input", "assets")
    os.makedirs(outfolder, exist_ok=True)

    # Check for texture stitching data
    textureMap = createTextureMap(root, infile, useProgrammerArt)

    root = scanPacksForTexture(root, infile)
    if useProgrammerArt:
        root = scanPacksForTexture(root, infile, "./input/programmer_art")

    outfile = os.path.splitext(os.path.join(outfolder, infile))[0] + ".png"
    if infile != outfile:
        try:
            stitchTexture(leaf, textureMap, root, infile, outfile)
        except IOError:
            print("Error while generating texture for '%s'" % infile)

def createTextureMap(root, infile, useProgrammerArt):
    textureMap = {}
    if os.path.isfile(os.path.join(root, infile.replace(".png", ".betterleaves.json"))):
        with open(os.path.join(root, infile.replace(".png", ".betterleaves.json")), "r") as f:
            json_data = json.load(f)
            if "textureStitching" in json_data:
                printOverride("Using texture stitching data from: " + f.name)
                # Create texture map from stitching data
                for key, value in json_data["textureStitching"].items():
                    if "-" in key:
                        for i in range(int(key.split("-")[0]), int(key.split("-")[1])+1):
                            textureMap[str(i)] = value
                    else:
                        textureMap[key] = value
                # Turn texture map into absolute paths
                for key, value in textureMap.items():
                    textureRoot = f"./input/assets/{value.split(':')[0]}/textures/"
                    textureFile = value.split(":")[1] + ".png"
                    if "/" in textureFile:
                        textureRoot += textureFile.rsplit("/")[0]
                        textureFile = textureFile[len(textureFile.rsplit("/")[0])+1:] # The rest of the string, starting behind the first '/'
                    textureRoot = scanPacksForTexture(textureRoot, textureFile)
                    if useProgrammerArt:
                        root = scanPacksForTexture(textureRoot, textureFile, "./input/programmer_art")
                    textureMap[key] = os.path.join(textureRoot, textureFile)
    return textureMap

def stitchTexture(leaf: LeafBlock, textureMap, root, infile, outfile):
    # First, let's open the regular texture
    vanilla = Image.open(os.path.join(root, infile))
    width, height = vanilla.size
    # Second, let's generate a transparent texture that's twice the size
    transparent = Image.new("RGBA", [int(2 * s) for s in vanilla.size], (255, 255, 255, 0))
    out = transparent.copy()

    # Now we paste the regular texture in a 3x3 grid, centered in the middle
    for x in range(-1, 2):
        for y in range(-1, 2):
            texture = vanilla
            index = (x + 2) + (y + 1) * 3 # Turns coordinates into a number from 1 to 9
            if str(index) in textureMap: # Load texture from texture stitching map
                texture = Image.open(textureMap[str(index)])
            out.paste(texture, (int(width / 2 + width * x), int(height / 2 + height * y)))

    # As the last step, we apply our custom mask to round the edges and smoothen things out
    mask_location = f"input/masks/{width}px" # If possible, use a mask designed for the texture's size
    if not os.path.isdir(mask_location) or len(os.listdir(mask_location)) == 0:
        mask_location = "input/masks/16px"
    random.seed(infile) # Use the filename as a seed. This ensures we always get the same mask per block.
    masks = list_files_alphabetically(mask_location)
    leaf.mask_index = random.randint(0, len(masks)-1) # Choose a random mask to get some variation between the different types of leaves
    mask_location += f"/{masks[leaf.mask_index]}"
    mask = Image.open(mask_location).convert('L').resize(out.size, resample=Image.NEAREST)
    out = Image.composite(out, transparent, mask)

    # Finally, we save the texture to the assets folder
    out.save(outfile, vanilla.format)
