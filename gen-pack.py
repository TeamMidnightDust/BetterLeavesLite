#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script can automatically generate blockstate and block model files, as well as textures for the Better Leaves Lite resourcepack."""

import argparse
import json
import os
import zipfile
from PIL import Image

def autoGen(notint_overrides):
    print("Generating assets...")
    for root, dirs, files in os.walk("./input"):
        for infile in files:
            if infile.endswith(".png") and (len(root.split("/")) > 3):
                namespace = root.split("/")[3]
                block_id = infile.replace(".png", "")
                print(namespace+":"+block_id)

                # Generate textures
                outfolder = root.replace("assets", "").replace("input", "assets")
                os.makedirs(outfolder, exist_ok=True)
                outfile = os.path.splitext(os.path.join(outfolder, infile))[0] + ".png"
                if infile != outfile:
                    try:
                        # First, let's open the regular texture
                        vanilla = Image.open(os.path.join(root, infile))
                        width, height = vanilla.size
                        # Second, let's generate a transparent texture that's twice the size
                        transparent = Image.new("RGBA", [int(2 * s) for s in vanilla.size], (255, 255, 255, 0))
                        out = transparent.copy()

                        # Now we paste the regular texture in a 3x3 grid, centered in the middle
                        for x in range(-1, 2):
                            for y in range(-1, 2):
                                out.paste(vanilla, (int(width / 2 + width * x), int(height / 2 + height * y)))

                        # As the last step, we apply our custom mask to round the edges and smoothen things out
                        mask = Image.open('input/mask.png').convert('L').resize(out.size)
                        out = Image.composite(out, transparent, mask)

                        # Finally, we save the texture to the assets folder
                        out.save(outfile, vanilla.format)
                    except IOError:
                        print("Error while generating texture for '%s'" % infile)

                # Generate blockstates & models

                # Check if the block appears in the notint overrides
                if (namespace+":"+block_id) in notint_overrides:
                    generateBlockstateAndModel(namespace, block_id, True)
                    generateItemModel(namespace, block_id)
                    print ("-> No tint")
                else:
                    generateBlockstateAndModel(namespace, block_id, False)

def generateBlockstateAndModel(mod_namespace, block_name, notint):

    # Create structure for blockstate file
    block_state_file = f"assets/{mod_namespace}/blockstates/{block_name}.json"
    block_state_data = {
        "variants": {
            "": []
        }
    }
    # Add four rotations for each of the four individual leaf models
    for i in range(1, 5):
        block_state_data["variants"][""] += { "model": f"{mod_namespace}:block/{block_name}{i}" }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 90 }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 180 }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 270 },

    # Create blockstates folder if it doesn't exist already
    if not os.path.exists("assets/{}/blockstates/".format(mod_namespace)):
        os.makedirs("assets/{}/blockstates/".format(mod_namespace))

    # Write blockstate file
    with open(block_state_file, "w") as f:
        json.dump(block_state_data, f, indent=4)


    # Create models folder if it doesn't exist already
    if not os.path.exists("assets/{}/models/block/".format(mod_namespace)):
        os.makedirs("assets/{}/models/block/".format(mod_namespace))

    base_model = "leaves"
    if (notint):
        base_model = "leaves_notint"
    # Create the four individual leaf models
    for i in range(1, 5):
        # Create structure for block model file
        block_model_file = f"assets/{mod_namespace}/models/block/{block_name}{i}.json"
        block_model_data = {
            "parent": f"block/{base_model}{i}",
            "textures": {
                "all": f"{mod_namespace}:block/{block_name}"
            }
        }
        with open(block_model_file, "w") as f:
            json.dump(block_model_data, f, indent=4)

def generateItemModel(mod_namespace, block_name):
    # Create models folder if it doesn't exist already
    if not os.path.exists("assets/{}/models/item/".format(mod_namespace)):
        os.makedirs("assets/{}/models/item/".format(mod_namespace))

    item_model_file = f"assets/{mod_namespace}/models/item/{block_name}.json"
    item_model_data = {
        "parent": f"{mod_namespace}:block/{block_name}1"
    }
    with open(item_model_file, "w") as f:
        json.dump(item_model_data, f, indent=4)

# See https://stackoverflow.com/a/1855118
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))



# This is the main entry point, executed when the script is run
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    description='This script can automatically generate files for the Better Leaves Lite resourcepack.',
                    epilog='Feel free to ask for help at http://discord.midnightdust.eu/')

    parser.add_argument('version', type=str)
    args = parser.parse_args()

    print(args)
    print()

    # Loads overrides from the json file
    f = open('./input/overrides.json')
    data = json.load(f)
    f.close()

    autoGen(data['noTint']);

    with zipfile.ZipFile('Better-Leaves-Lite-'+args.version+".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir('assets/', zipf)
        zipf.write('pack.mcmeta')
        zipf.write('pack.png')
        zipf.write('LICENSE')
        zipf.write('README.md')