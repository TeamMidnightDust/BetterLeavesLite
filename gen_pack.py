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

minify = False

# Utility functions
def printGreen(out): print("\033[92m{}\033[00m".format(out))
def printCyan(out): print("\033[96m{}\033[00m" .format(out))
def printOverride(out): print(" -> {}".format(out))
def dumpJson(data, f): json.dump(data, f, separators=(',', ':')) if minify else json.dump(data, f, indent=4)

class BlockStateData:
    def __init__(self, namespace, block_name, state):
        self.namespace = namespace
        self.block_name = block_name
        self.state = state
    def fromFile(leaf, root, infile):
        with open(os.path.join(root, infile), "r") as f:
            printOverride("Loading blockstate data from: "+f.name)
            return BlockStateData.fromJson(leaf, json.load(f).get("blockStateData"))
    def fromJson(leaf, data): return BlockStateData(data["block"].split(":")[0], data["block"].split(":")[1], data["state"]) if "block" in data else BlockStateData(leaf.getId().split(":")[0], leaf.getId().split(":")[1], data["state"])

class LeafBlock:
    def __init__(self, namespace, block_name, texture_name):
        self.namespace = namespace
        self.block_name = block_name
        self.texture_name = texture_name
    base_model = "leaves"
    has_carpet = False
    has_no_tint = False
    has_texture_override = False
    should_generate_item_model = False
    use_legacy_model = False
    texture_prefix = ""
    overlay_texture_id = ""
    block_id_override = None
    texture_id_override = None
    dynamictrees_namespace = None
    blockstate_data = None
    def getId(self):
        if (self.block_id_override != None): return self.block_id_override
        return self.namespace+":"+self.block_name
    def getTextureId(self):
        if (self.texture_id_override != None): return self.texture_id_override
        return self.namespace+":block/"+self.texture_prefix+self.texture_name
class CarpetBlock:
    def __init__(self, carpet_id, leaf):
        self.carpet_id = carpet_id
        self.leaf = leaf
        if (leaf.has_no_tint): self.base_model = "leaf_carpet_notint"
    base_model = "leaf_carpet"

# This is where the magic happens
def autoGen(jsonData, args):
    notint_overrides = jsonData["noTint"]
    block_texture_overrides = jsonData["blockTextures"]
    overlay_textures = jsonData["overlayTextures"]
    block_id_overrides = jsonData["blockIds"]
    leaves_with_carpet = jsonData["leavesWithCarpet"]
    dynamictrees_namespaces = jsonData["dynamicTreesNamespaces"]
    generate_itemmodels_overrides = jsonData["generateItemModels"]
    block_state_copies = jsonData["blockStateCopies"]
    print("Generating assets...")
    if (os.path.exists("./assets")): shutil.rmtree("./assets")
    copy_tree("./base/assets/", "./assets/")
    if minify: minifyJsonFiles()

    filecount = 0
    if (args.programmer): unpackTexturepacks("./input/programmer_art")
    unpackTexturepacks()
    unpackMods()
    scanModsForTextures()

    for root, dirs, files in os.walk("./input/assets"):
        for infile in files:
            if infile.endswith(".png") and (len(root.split("/")) > 3):
                texture_name = infile.replace(".png", "")

                leaf = LeafBlock(root.split("/")[3], texture_name, texture_name)

                # Handle leaf textures in subfolders
                if (len(root.split("/")) > 6):
                    leaf.texture_prefix = root.split("/")[6]+"/"
                    if (leaf.block_name == "leaves"): # For mods that use a structure like "texture/woodtype/leaves.png"
                        leaf.block_name = leaf.texture_prefix.replace("/", "_")+leaf.block_name
                        printGreen(leaf.getId())
                        printOverride("Auto-redirected from "+leaf.getId())
                    else: # For mods that use a structure like "texture/natural/some_leaves.png"
                        printGreen(leaf.getId())
                        printOverride("Prefix: "+ leaf.texture_prefix);
                else: printGreen(leaf.getId())

                # We don't want to generate assets for overlay textures
                if (leaf.getTextureId()) in overlay_textures.values(): 
                    printOverride("Skipping overlay texture")
                    continue 

                texture = Image.open(os.path.join(root, infile))
                leaf.use_legacy_model = texture.size[0] != texture.size[1]
                if leaf.use_legacy_model: printOverride("Animated – using legacy model")
                if args.legacy: 
                    leaf.use_legacy_model = True
                    printOverride("Using legacy model as requested")

                # Generate texture
                if not leaf.use_legacy_model: generateTexture(root, infile, args.programmer)

                # Set block id and apply overrides
                if leaf.getId() in block_id_overrides:
                    leaf.block_id_override = block_id_overrides[leaf.getId()]
                    printOverride("ID Override: "+leaf.getId())

                # Set texture id and apply overrides
                leaf.has_texture_override = leaf.getId() in block_texture_overrides
                if leaf.has_texture_override:
                    leaf.texture_id_override = block_texture_overrides[leaf.getId()]
                    printOverride("Texture Override: "+leaf.getTextureId())

                # Check if the block appears in the notint overrides
                leaf.has_no_tint = leaf.getId() in notint_overrides
                if leaf.use_legacy_model: 
                    leaf.base_model = "leaves_legacy"
                elif leaf.has_no_tint:
                    leaf.base_model = "leaves_notint"
                    printOverride("No tint")

                # Check if the block has an additional overlay texture
                if leaf.getId() in overlay_textures:
                    leaf.base_model = "leaves_overlay"
                    leaf.overlay_texture_id = overlay_textures[leaf.getId()]
                    printOverride("Has overlay texture: "+leaf.overlay_texture_id) 

                # Check if the block has a dynamic trees addon namespace
                
                if (leaf.namespace) in dynamictrees_namespaces:
                    leaf.dynamictrees_namespace = dynamictrees_namespaces[leaf.namespace]

                # Check if the block should generate an item model
                if leaf.getId() in generate_itemmodels_overrides:
                    leaf.should_generate_item_model = True
                    printOverride("Also generating item model")
                
                # Check for blockstate data
                if infile.replace(".png", ".betterleaves.json") in files:
                    leaf.blockstate_data = BlockStateData.fromFile(leaf, root, infile.replace(".png", ".betterleaves.json"))

                # Generate blockstates & models
                generateBlockstate(leaf, block_state_copies)
                generateBlockModels(leaf)
                generateItemModel(leaf)

                # Certain mods contain leaf carpets.
                # Because we change the leaf texture, we need to fix the carpet models.
                if (leaf.getId()) in leaves_with_carpet:
                    carpet_ids = leaves_with_carpet[leaf.getId()]
                    if not isinstance(carpet_ids, list): carpet_ids = [carpet_ids] # In case only one carpet is provided (as a string), turn it into a list
                    for carpet_id in carpet_ids:
                        carpet = CarpetBlock(carpet_id, leaf)
                        generateCarpetAssets(carpet)
                        printOverride(f"Generating leaf carpet: {carpet.carpet_id}")

                filecount += 1
    # End of autoGen
    print()
    if (args.programmer): cleanupTexturepacks("./input/programmer_art")
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
                    print(f"Found texture {assetpath}/{infile} in mod {modid}")
                    inputfolder = os.path.join("./input/assets/", assetpath)
                    os.makedirs(inputfolder, exist_ok=True)
                    shutil.copyfile(os.path.join(root, infile), os.path.join(inputfolder, infile))


def unpackTexturepacks(rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for infile in files:
            if infile.endswith(".zip"):
                print("Unpacking texturepack: "+infile)
                zf = zipfile.ZipFile(os.path.join(root, infile), 'r')
                zf.extractall(os.path.join(root, infile.replace(".zip", "_temp")))
                zf.close()

def cleanupTexturepacks(rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for folder in dirs:
            if folder.endswith("_temp"):
                shutil.rmtree(os.path.join(root, folder))

def scanPacksForTexture(baseRoot, baseInfile, rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for infile in files:
            if "assets" in root and "assets" in baseRoot:
                if infile.endswith(".png") and (len(root.split("/")) > 3) and (baseInfile == infile) and (root.split("assets")[1] == baseRoot.split("assets")[1]):
                    printCyan(" Using texture from: " + root.split("assets")[0].replace(rootFolder, ""))
                    return root;
    return baseRoot

def generateTexture(root, infile, useProgrammerArt=False):
    outfolder = root.replace("assets", "").replace("input", "assets")
    os.makedirs(outfolder, exist_ok=True)

    # Check for texture stitching data
    textureMap = {}
    if os.path.isfile(os.path.join(root, infile.replace(".png", ".betterleaves.json"))):
        with open(os.path.join(root, infile.replace(".png", ".betterleaves.json")), "r") as f:
            json_data = json.load(f)
            if "textureStitching" in json_data:
                printOverride("Using texture stitching data from: " + f.name)
                # Create texture map from stitching data
                for key, value in json_data["textureStitching"].items():
                    if "-" in key:
                        for i in range(int(key.split("-")[0]), int(key.split("-")[1])+1): textureMap[str(i)] = value
                    else: textureMap[key] = value
                # Turn texture map into absolute paths
                for key, value in textureMap.items():
                    textureRoot = f"./input/assets/{value.split(':')[0]}/textures/"
                    textureFile = value.split(":")[1] + ".png"
                    if "/" in textureFile: 
                        textureRoot += textureFile.rsplit("/")[0]
                        textureFile = textureFile.rsplit("/")[1]
                    textureRoot = scanPacksForTexture(textureRoot, textureFile)
                    if useProgrammerArt: root = scanPacksForTexture(textureRoot, textureFile, "./input/programmer_art")
                    textureMap[key] = os.path.join(textureRoot, textureFile)

    root = scanPacksForTexture(root, infile)
    if useProgrammerArt: root = scanPacksForTexture(root, infile, "./input/programmer_art")

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
                    texture = vanilla
                    index = (x + 2) + (y + 1) * 3 # Turns coordinates into a number from 1 to 9
                    if str(index) in textureMap: # Load texture from texture stitching map
                        texture = Image.open(textureMap[str(index)])
                    out.paste(texture, (int(width / 2 + width * x), int(height / 2 + height * y)))

            # As the last step, we apply our custom mask to round the edges and smoothen things out
            mask = Image.open('input/mask.png').convert('L').resize(out.size, resample=Image.NEAREST)
            out = Image.composite(out, transparent, mask)

            # Finally, we save the texture to the assets folder
            out.save(outfile, vanilla.format)
        except IOError:
            print("Error while generating texture for '%s'" % infile)


def generateBlockstate(leaf, block_state_copies):
    mod_namespace = leaf.getId().split(":")[0]
    block_name = leaf.getId().split(":")[1]

    block_state_namespace = mod_namespace
    block_state_name = block_name

    state = ""
    if leaf.blockstate_data != None: # In case custom blockstate data is defined
        block_state_namespace = leaf.blockstate_data.namespace
        block_state_name = leaf.blockstate_data.block_name
        state = leaf.blockstate_data.state

    # Create structure for blockstate file
    block_state_file = f"assets/{block_state_namespace}/blockstates/{block_state_name}.json"
    block_state_data = {
        "variants": {
            f"{state}": []
        }
    }
    if os.path.exists(block_state_file): # In case the blockstate file already exists, we want to add to it
        with open(block_state_file, "r") as f:
            block_state_data = json.load(f)
            block_state_data["variants"][state] = []
    
    # Add four rotations for each of the four individual leaf models
    for i in range(1, 5):
        block_state_data["variants"][state] += { "model": f"{mod_namespace}:block/{block_name}{i}" }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 90 }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 180 }, { "model": f"{mod_namespace}:block/{block_name}{i}", "y": 270 },

    # Create blockstates folder if it doesn't exist already
    os.makedirs("assets/{}/blockstates/".format(block_state_namespace), exist_ok=True)

    # Write blockstate file
    with open(block_state_file, "w") as f:
        dumpJson(block_state_data, f)
    
    # Do the same for the dynamic trees namespace
    if leaf.dynamictrees_namespace != None:
        dyntrees_block_state_file = f"assets/{leaf.dynamictrees_namespace}/blockstates/{block_name}.json"
        os.makedirs("assets/{}/blockstates/".format(leaf.dynamictrees_namespace), exist_ok=True)

        # Write blockstate file
        with open(dyntrees_block_state_file, "w") as f:
            dumpJson(block_state_data, f)
    
    # Additional block state copies
    if (leaf.getId()) in block_state_copies:
        block_state_copy_ids = block_state_copies[leaf.getId()]
        if not isinstance(block_state_copy_ids, list): block_state_copy_ids = [block_state_copy_ids] # In case only one blockstate is provided (as a string), turn it into a list
        for block_state_copy_id in block_state_copy_ids:
            block_state_copy_namespace = block_state_copy_id.split(":")[0]
            block_state_copy_name = block_state_copy_id.split(":")[1]

            block_state_copy_file = f"assets/{block_state_copy_namespace}/blockstates/{block_state_copy_name}.json"
            os.makedirs("assets/{}/blockstates/".format(block_state_copy_namespace), exist_ok=True)

            # Write blockstate file
            with open(block_state_copy_file, "w") as f:
                dumpJson(block_state_data, f)
                printOverride(f"Writing blockstate copy: {block_state_copy_id}")
    

def generateBlockModels(leaf):
    mod_namespace = leaf.getId().split(":")[0]
    block_name = leaf.getId().split(":")[1]
    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/block/".format(mod_namespace), exist_ok=True)

    # Create the four individual leaf models
    for i in range(1, 5):
        # Create structure for block model file
        block_model_file = f"assets/{mod_namespace}/models/block/{block_name}{i}.json"
        block_model_data = {
            "parent": f"betterleaves:block/{leaf.base_model}{i}",
            "textures": {
                "all": f"{leaf.getTextureId()}"
            }
        }
        # Add overlay texture on request
        if (leaf.overlay_texture_id != ""):
            block_model_data["textures"]["overlay"] = leaf.overlay_texture_id

        # Write block model file
        with open(block_model_file, "w") as f:
            dumpJson(block_model_data, f)

def generateItemModel(leaf):
    mod_namespace = leaf.getId().split(":")[0]
    block_name = leaf.getId().split(":")[1]

    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/block/".format(mod_namespace), exist_ok=True)

    block_item_model_file = f"assets/{mod_namespace}/models/block/{block_name}.json"

    if leaf.has_texture_override: # Used for items that have a different texture than the block model
        item_model_data = {
            "parent": f"betterleaves:block/{leaf.base_model}",
            "textures": {
                "all": f"{mod_namespace}:block/{block_name}"
            }
        }
    else: # By default, the regular block texture is used
        item_model_data = {
            "parent": f"betterleaves:block/{leaf.base_model}",
            "textures": {
                "all": f"{leaf.getTextureId()}"
            }
        }
    # Add overlay texture on request
    if (leaf.overlay_texture_id != ""):
        item_model_data["textures"]["overlay"] = leaf.overlay_texture_id
    
    with open(block_item_model_file, "w") as f:
        dumpJson(item_model_data, f)
    
    if leaf.should_generate_item_model:
        # Create models folder if it doesn't exist already
        os.makedirs("assets/{}/models/item/".format(mod_namespace), exist_ok=True)
        
        item_model_file = f"assets/{mod_namespace}/models/item/{block_name}.json"
        with open(item_model_file, "w") as f:
            dumpJson(item_model_data, f)

def generateCarpetAssets(carpet):
    mod_namespace = carpet.carpet_id.split(":")[0]
    block_name = carpet.carpet_id.split(":")[1]
    # Create blockstate folder if it doesn't exist already
    os.makedirs("assets/{}/blockstates/".format(mod_namespace), exist_ok=True)

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
        dumpJson(block_state_data, f)

    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/block/".format(mod_namespace), exist_ok=True)

    # Create structure for block model file
    block_model_file = f"assets/{mod_namespace}/models/block/{block_name}.json"
    block_model_data = {
        "parent": f"betterleaves:block/{carpet.base_model}",
        "textures": {
            "wool": f"{carpet.leaf.getTextureId()}"
        }
    }
    # Save the carpet block model file
    with open(block_model_file, "w") as f:
        dumpJson(block_model_data, f)

def minifyJsonFiles(rootDir="./assets"):
    for root, dirs, files in os.walk(rootDir):
        for infile in files:
            if infile.endswith(".json"):
                minifyExistingJson(root, infile)
def minifyExistingJson(root, infile):
    with open(os.path.join(root, infile), "r") as rf:
        data = json.load(rf)
        with open(os.path.join(root, infile), "w") as wf:
            json.dump(data, wf, separators=(',', ':'))

def writeMetadata(args):
    edition = args.edition
    if isinstance(edition, list): edition = " ".join(args.edition)
    with open("./input/pack.mcmeta") as infile, open("pack.mcmeta", "w") as outfile:
        for line in infile:
            line = line.replace("${version}", args.version).replace("${edition}", edition).replace("${year}", str(time.localtime().tm_year))
            outfile.write(line)

# See https://stackoverflow.com/a/1855118
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

# Creates a compressed zip file
def makeZip(filename):
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
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
    parser.add_argument('edition', nargs="*", type=str, default="§cCustom Edition", help="Define your edition name")
    parser.add_argument('--legacy', '-l', action='store_true', help="Use legacy models (from 8.1) for all leaves")
    parser.add_argument('--programmer', '-p', action='store_true', help="Use programmer art textures")
    parser.add_argument('--minify', '-m', action='store_true', help="Minify all JSON output files")
    args = parser.parse_args()

    print(f"Arguments: {args}")
    print()
    print("Motschen's Better Leaves Lite")
    print("https://github.com/TeamMidnightDust/BetterLeavesLite")
    print()
    if args.minify: minify = True

    # Loads overrides from the json file
    f = open('./input/overrides.json')
    data = json.load(f)
    f.close()

    autoGen(data, args);
    writeMetadata(args)
    print()
    print("Zipping it up...")
    makeZip(f"Better-Leaves-{args.version}.zip" if not args.programmer else f"Better-Leaves-(Programmer-Art)-{args.version}.zip");
    print("Done!")
    print("--- Finished in %s seconds ---" % (round((time.perf_counter() - start_time)*1000)/1000))
    