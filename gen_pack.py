#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script can automatically generate blockstate and block model files, as well as textures for the Better Leaves Lite resourcepack."""

import argparse
import json
import os
import zipfile
import shutil
import time
from PIL import Image
from distutils.dir_util import copy_tree

# Utility functions
def printGreen(out): print("\033[92m{}\033[00m".format(out))
def printCyan(out): print("\033[96m{}\033[00m" .format(out))
def printOverride(out): print(" -> {}".format(out))

# This is where the magic happens
def autoGen(jsonData):
    notint_overrides = jsonData["noTint"]
    block_texture_overrides = jsonData["blockTextures"]
    overlay_textures = jsonData["overlayTextures"]
    block_id_overrides = jsonData["blockIds"]
    leaves_with_carpet = jsonData["leavesWithCarpet"]
    dynamictrees_namespaces = jsonData["dynamicTreesNamespaces"]
    print("Generating assets...")
    if (os.path.exists("./assets")): shutil.rmtree("./assets")
    copy_tree("./base/assets/", "./assets/")
    filecount = 0
    unpackTexturepacks()
    unpackMods()
    scanModsForTextures()

    for root, dirs, files in os.walk("./input/assets"):
        for infile in files:
            if infile.endswith(".png") and (len(root.split("/")) > 3):
                namespace = root.split("/")[3]
                texture_name = infile.replace(".png", "")
                block_name = texture_name

                # Handle leaf textures in subfolders
                texture_prefix = ""
                if (len(root.split("/")) > 6):
                    texture_prefix = root.split("/")[6]+"/"
                    if (block_name == "leaves"): # For mods that use a structure like "texture/woodtype/leaves.png"
                        block_name = texture_prefix.replace("/", "_")+block_name
                        printGreen(namespace+":"+block_name)
                        printOverride("Auto-redirected from "+namespace+":"+texture_name)
                    else: # For mods that use a structure like "texture/natural/some_leaves.png"
                        printGreen(namespace+":"+block_name)
                        printOverride("Prefix: "+ texture_prefix);
                else: printGreen(namespace+":"+block_name)

                # We don't want to generate assets for overlay textures
                if (namespace+":block/"+texture_prefix+texture_name) in overlay_textures.values(): 
                    printOverride("Skipping overlay texture")
                    continue 

                texture = Image.open(os.path.join(root, infile))
                is_animated = texture.size[0] != texture.size[1]

                # Generate texture
                if not is_animated: generateTexture(root, infile)

                # Set block id and apply overrides
                block_id = namespace+":"+block_name
                if block_id in block_id_overrides:
                    block_id = block_id_overrides[block_id]
                    printOverride("ID Override: "+block_id)

                # Set texture id and apply overrides
                texture_id = namespace+":block/"+texture_prefix+texture_name
                has_texture_override = (block_id) in block_texture_overrides
                if has_texture_override:
                    texture_id = block_texture_overrides[block_id]
                    printOverride("Texture Override: "+texture_id)

                base_model = "leaves"
                # Check if the block appears in the notint overrides
                hasNoTint = block_id in notint_overrides
                if is_animated: 
                    base_model = "leaves_legacy"
                    printOverride("Animated – using legacy model")
                elif hasNoTint:
                    base_model = "leaves_notint"
                    printOverride("No tint")

                # Check if the block has an additional overlay texture
                overlay_texture_id = ""
                if block_id in overlay_textures:
                    base_model = "leaves_overlay"
                    overlay_texture_id = overlay_textures[block_id]
                    printOverride("Has overlay texture: "+overlay_texture_id) 

                # Check if the block has a dynamic trees addon namespace
                dynamictrees_namespace = None
                if (namespace) in dynamictrees_namespaces:
                    dynamictrees_namespace = dynamictrees_namespaces[namespace]

                # Generate blockstates & models
                generateBlockstate(block_id, dynamictrees_namespace)
                generateBlockModels(block_id, base_model, texture_id, overlay_texture_id)
                generateItemModel(block_id, has_texture_override)

                # Certain mods contain leaf carpets.
                # Because we change the leaf texture, we need to fix the carpet models.
                if (block_id) in leaves_with_carpet:
                    carpet_id = leaves_with_carpet[block_id]
                    generateCarpetAssets(carpet_id, hasNoTint, texture_id)
                    printOverride(f"Generating leaf carpet: {carpet_id}")

                filecount += 1
    # End of autoGen
    print()
    cleanupTexturepacks()
    cleanupMods()
    printCyan("Processed {} leaf blocks".format(filecount))

def unpackMods():
    for root, dirs, files in os.walk("./input/mods"):
        for infile in files:
            if infile.endswith(".jar"):
                print("Unpacking mod: "+infile)
                zf = zipfile.ZipFile(os.path.join(root, infile), 'r')
                zf.extractall(os.path.join(root, infile.replace(".jar", "_temp")))
                zf.close()

def cleanupMods():
    if (os.path.exists("./input/mods")): shutil.rmtree("./input/mods")
    os.makedirs("./input/mods")

def scanModsForTextures():
    for root, dirs, files in os.walk("./input/mods"):
        for infile in files:
            if len(root.split("assets")) > 1:
                assetpath = root.split("assets")[1][1:]
                modid = assetpath.split("textures")[0].replace("/", "")
                if "textures/block" in root and infile.endswith(".png") and "leaves" in infile:
                    print(f"Found texture {assetpath+"/"+infile} in mod {modid}")
                    inputfolder = os.path.join("./input/assets/", assetpath)
                    os.makedirs(inputfolder, exist_ok=True)
                    shutil.copyfile(os.path.join(root, infile), os.path.join(inputfolder, infile))


def unpackTexturepacks():
    for root, dirs, files in os.walk("./input/texturepacks"):
        for infile in files:
            if infile.endswith(".zip"):
                print("Unpacking texturepack: "+infile)
                zf = zipfile.ZipFile(os.path.join(root, infile), 'r')
                zf.extractall(os.path.join(root, infile.replace(".zip", "_temp")))
                zf.close()

def cleanupTexturepacks():
    for root, dirs, files in os.walk("./input/texturepacks"):
        for folder in dirs:
            if folder.endswith("_temp"):
                shutil.rmtree(os.path.join(root, folder))

def scanPacksForTexture(baseRoot, baseInfile):
    for root, dirs, files in os.walk("./input/texturepacks"):
        for infile in files:
            if "assets" in root and "assets" in baseRoot:
                if infile.endswith(".png") and (len(root.split("/")) > 3) and (baseInfile == infile) and (root.split("assets")[1] == baseRoot.split("assets")[1]):
                    printCyan(" Using texture from: " + root.split("assets")[0].replace("./input/texturepacks/", ""))
                    return root;
    return baseRoot

def generateTexture(root, infile):
    outfolder = root.replace("assets", "").replace("input", "assets")
    os.makedirs(outfolder, exist_ok=True)

    root = scanPacksForTexture(root, infile)

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
            mask = Image.open('input/mask.png').convert('L').resize(out.size, resample=Image.NEAREST)
            out = Image.composite(out, transparent, mask)

            # Finally, we save the texture to the assets folder
            out.save(outfile, vanilla.format)
        except IOError:
            print("Error while generating texture for '%s'" % infile)


def generateBlockstate(block_id, dynamictrees_namespace):
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
    os.makedirs("assets/{}/blockstates/".format(mod_namespace), exist_ok=True)

    # Write blockstate file
    with open(block_state_file, "w") as f:
        json.dump(block_state_data, f, indent=4)
    
    # Do the same for the dynamic trees namespace
    if dynamictrees_namespace != None:
        dyntrees_block_state_file = f"assets/{dynamictrees_namespace}/blockstates/{block_name}.json"
        os.makedirs("assets/{}/blockstates/".format(dynamictrees_namespace), exist_ok=True)

        # Write blockstate file
        with open(dyntrees_block_state_file, "w") as f:
            json.dump(block_state_data, f, indent=4)
    

def generateBlockModels(block_id, base_model, texture_id, overlay_texture_id):
    mod_namespace = block_id.split(":")[0]
    block_name = block_id.split(":")[1]
    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/block/".format(mod_namespace), exist_ok=True)

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
        # Add overlay texture on request
        if (overlay_texture_id != ""):
            block_model_data["textures"]["overlay"] = overlay_texture_id

        # Write block model file
        with open(block_model_file, "w") as f:
            json.dump(block_model_data, f, indent=4)

def generateItemModel(block_id, override_block_texture=False):
    mod_namespace = block_id.split(":")[0]
    block_name = block_id.split(":")[1]

    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/item/".format(mod_namespace), exist_ok=True)

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
    # Save the carpet block model file
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

# Creates a compressed zip file
def makeZip(version):
    with zipfile.ZipFile('Better-Leaves-Lite-'+version+".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir('assets/', zipf)
        zipf.write('pack.mcmeta')
        zipf.write('pack.png')
        zipf.write('LICENSE')
        zipf.write('README.md')


# This is the main entry point, executed when the script is run
if __name__ == '__main__':
    start_time = time.perf_counter()
    parser = argparse.ArgumentParser(
                    description='This script can automatically generate files for the Better Leaves Lite resourcepack.',
                    epilog='Feel free to ask for help at http://discord.midnightdust.eu/')

    parser.add_argument('version', type=str)
    args = parser.parse_args()

    print(f"Arguments: {args}")
    print()
    print("Motschen's Better Leaves Lite")
    print("https://github.com/TeamMidnightDust/BetterLeavesLite")
    print()

    # Loads overrides from the json file
    f = open('./input/overrides.json')
    data = json.load(f)
    f.close()

    autoGen(data);
    print()
    print("Zipping it up...")
    makeZip(args.version);
    print("Done!")
    print("--- Finished in %s seconds ---" % (round((time.perf_counter() - start_time)*1000)/1000))
    