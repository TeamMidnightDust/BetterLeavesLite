import os
from PIL import Image

# Local imports
from src.texturepack_utils import scanPacksForTexture
from src.utilities import list_files_alphabetically, printOverride

def generateSnowyOverlay(useProgrammerArt=False):
    outfolder = "assets/betterleaves/textures/block/"
    os.makedirs(outfolder, exist_ok=True)

    try:
        stitchTexture(outfolder, useProgrammerArt)
    except IOError:
        print("Error while generating snow overlay texture")


def stitchTexture(outfolder, useProgrammerArt):
    # First, let's open the regular texture
    infile = "block/snow.png"
    root = scanPacksForTexture("input/assets/minecraft/textures/", infile)
    if useProgrammerArt:
        root = scanPacksForTexture(root, infile, "./input/programmer_art")
    top = Image.open(os.path.join(root, infile))
    side = generateSnowySideTexture(useProgrammerArt)
    width, height = top.size
    # Second, let's generate a transparent texture that's twice the size
    transparent = Image.new("RGBA", [int(2 * s) for s in top.size], (255, 255, 255, 0))
    out = transparent.copy()

    for x in range(-1, 2):
        out.paste(top, (int(width / 2 + width * x), int(height / 2 + height * -1)))
        out.paste(side, (int(width / 2 + width * x), int(height / 2)))

    # As the last step, we apply our custom mask to round the edges and smoothen things out
    mask_location = f"input/masks/{width}px/snowy" # If possible, use a mask designed for the texture's size
    if not os.path.isdir(mask_location) or len(os.listdir(mask_location)) == 0:
        mask_location = "input/masks/16px/snowy"
    masks = list_files_alphabetically(mask_location)
    for mask_index in range(0, len(masks)):
        mask = Image.open(os.path.join(mask_location, masks[mask_index])).convert('L').resize(out.size, resample=Image.NEAREST)
        output = Image.composite(out, transparent, mask)

        # Finally, we save the texture to the assets folder
        outfile = os.path.splitext(os.path.join(outfolder, f"snowy_overlay{mask_index}"))[0] + ".png"
        printOverride(f"Created mask: {mask_index} for {masks[mask_index]}")
        output.save(outfile, top.format)

def generateSnowySideTexture(useProgrammerArt):
    infile = "block/grass_block_snow.png"
    root = scanPacksForTexture("input/assets/minecraft/textures/", infile)
    if useProgrammerArt:
        root = scanPacksForTexture(root, infile, "./input/programmer_art")
    side = Image.open(os.path.join(root, infile))
    transparent = Image.new("RGBA",side.size, (255, 255, 255, 0))
    transparent.paste(side)
    side = transparent

    width = side.size[0]
    height = side.size[1]
    for i in range(0,width):# process all pixels
        for j in range(0,height):
            data = side.getpixel((i,j))
            if data[0] < 190 : # Set to transparent if the pixel is too dark to be considered part of the snow
                side.putpixel((i,j),(0, 0, 0, 0))
    return side
