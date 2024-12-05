#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script can automatically generate blockstate and block model files, as well as textures for the Better Leaves Lite resourcepack."""

import argparse
import json
import os
import zipfile
import shutil
from PIL import Image
from distutils.dir_util import copy_tree

def autoGen(jsonData):
    notint_overrides = jsonData["noTint"]
    block_texture_overrides = jsonData["blockTextures"]
    overlay_textures = jsonData["overlayTextures"]
    block_id_overrides = jsonData["blockIds"]
    leaves_with_carpet = jsonData["leavesWithCarpet"]
    print("Generating assets...")
    if (os.path.exists("./assets")): shutil.rmtree("./assets")
    copy_tree("./base/assets/", "./assets/")

    for root, dirs, files in os.walk("./input"):
        for infile in files:
            if infile.endswith(".png") and (len(root.split("/")) > 3):
                namespace = root.split("/")[3]
                block_name = infile.replace(".png", "")
                if (namespace+":block/"+block_name) in overlay_textures.values(): continue # We don't want to generate assets for overlay textures

                print(namespace+":"+block_name)
                texture_prefix = ""
                if (len(root.split("/")) > 6):
                    texture_prefix = root.split("/")[6]+"/"
                    print("-> Prefix: "+ texture_prefix);

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

                # Set block id and apply overrides
                block_id = namespace+":"+block_name
                if block_id in block_id_overrides:
                    block_id = block_id_overrides[block_id]

                # Set texture id and apply overrides
                texture_id = namespace+":block/"+block_name

                has_texture_override = (block_id) in block_texture_overrides
                if has_texture_override:
                    texture_id = block_texture_overrides[block_id]
                    print ("-> Texture Override: "+texture_id)
                else: 
                    if (texture_prefix != ""):
                        texture_id = namespace+":block/"+texture_prefix+block_name

                base_model = "leaves"
                
                # Check if the block appears in the notint overrides
                hasNoTint = block_id in notint_overrides
                if hasNoTint:
                    base_model = "leaves_notint"
                    print ("-> No tint")

                # Check if the block has an additional overlay texture
                overlay_texture_id = ""
                if block_id in overlay_textures:
                    base_model = "leaves_overlay"
                    overlay_texture_id = overlay_textures[block_id]
                    print ("-> Has overlay texture: "+overlay_texture_id) 

                # Generate blockstates & models
                generateBlockstateAndModel(block_id, base_model, texture_id, overlay_texture_id)
                generateItemModel(block_id, has_texture_override)

                if (block_id) in leaves_with_carpet:
                    carpet_id = leaves_with_carpet[block_id]
                    generateCarpetAssets(carpet_id, hasNoTint, texture_id)
                    print (f"-> Also generating leaf carpet: {carpet_id}")

def generateBlockstateAndModel(block_id, base_model, texture_id, overlay_texture_id):
    mod_namespace = block_id.split(":")[0]
    block_name = block_id.split(":")[1]

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

    # Create the four individual leaf models
    for i in range(1, 5):
        # Create structure for block model file
        block_model_file = f"assets/{mod_namespace}/models/block/{block_name}{i}.json"
        block_model_data = {
            "parent": f"betterleaves:block/{base_model}{i}",
            "textures": {
                "all": f"{texture_id}"
            }
        }
        if (overlay_texture_id != ""):
            block_model_data["textures"]["overlay"] = overlay_texture_id
        with open(block_model_file, "w") as f:
            json.dump(block_model_data, f, indent=4)

def generateItemModel(block_id, override_block_texture=False):
    mod_namespace = block_id.split(":")[0]
    block_name = block_id.split(":")[1]

    # Create models folder if it doesn't exist already
    if not os.path.exists("assets/{}/models/item/".format(mod_namespace)):
        os.makedirs("assets/{}/models/item/".format(mod_namespace))

    item_model_file = f"assets/{mod_namespace}/models/item/{block_name}.json"

    if override_block_texture: # Used for items that have a different texture than the block model
        item_model_data = {
            "parent": f"{mod_namespace}:block/{block_name}1",
            "textures": {
                "all": f"{mod_namespace}:block/{block_name}"
            }
        }
    else: # By default, the regular block model is used
        item_model_data = {
            "parent": f"{mod_namespace}:block/{block_name}1"
        }
    
    with open(item_model_file, "w") as f:
        json.dump(item_model_data, f, indent=4)

def generateCarpetAssets(carpet_id, notint, texture_id):
    mod_namespace = carpet_id.split(":")[0]
    block_name = carpet_id.split(":")[1]

    # Create structure for blockstate file
    block_state_file = f"assets/{mod_namespace}/blockstates/{block_name}.json"
    block_state_data = {
        "variants": {
            "": []
        }
    }
    # Add four rotations for the carpet model
    block_state_data["variants"][""] += { "model": f"{mod_namespace}:block/{block_name}" }, { "model": f"{mod_namespace}:block/{block_name}", "y": 90 }, { "model": f"{mod_namespace}:block/{block_name}", "y": 180 }, { "model": f"{mod_namespace}:block/{block_name}", "y": 270 },

    # Write blockstate file
    with open(block_state_file, "w") as f:
        json.dump(block_state_data, f, indent=4)

    base_model = "leaf_carpet"
    if (notint):
        base_model = "leaf_carpet_notint"

    # Create structure for block model file
    block_model_file = f"assets/{mod_namespace}/models/block/{block_name}.json"
    block_model_data = {
        "parent": f"betterleaves:block/{base_model}",
        "textures": {
            "wool": f"{texture_id}"
        }
    }
    with open(block_model_file, "w") as f:
        json.dump(block_model_data, f, indent=4)

# See https://stackoverflow.com/a/1855118
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def makeZip(version):
    with zipfile.ZipFile('Better-Leaves-Lite-'+version+".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir('assets/', zipf)
        zipf.write('pack.mcmeta')
        zipf.write('pack.png')
        zipf.write('LICENSE')
        zipf.write('README.md')



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

    autoGen(data);
    makeZip(args.version);
    