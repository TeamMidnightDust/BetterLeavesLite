# Depencency imports
import os
import shutil
from PIL import Image
from setuptools._distutils.dir_util import copy_tree

# Local imports
from src.data.leafblock import LeafBlock
from src.data.carpetblock import CarpetBlock
from src.mod_utils import unpackMods, cleanupMods, scanModsForTextures
from src.texturepack_utils import unpackTexturepacks, cleanupTexturepacks
from src.utilities import printCyan, printGreen, printOverride
from src.texture_generator import generateTexture
from src.model_generator import generateBlockModels, generateItemModel
from src.blockstate_generator import generateBlockstate
from src.carpet_generator import generateCarpetAssets
from src.json_utils import minifyJsonFiles, minify
from src.betterleaves_json import applyJson

# This is where the magic happens
def autoGen(jsonData, args):
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
                filecount += processLeaf(root, files, infile, jsonData, args)

    print()
    if (args.programmer): cleanupTexturepacks("./input/programmer_art")
    cleanupTexturepacks()
    cleanupMods()
    printCyan("Processed {} leaf blocks".format(filecount))

def processLeaf(root, files, infile, jsonData, args) -> int:
    texture_name = infile.replace(".png", "")
    leaf = LeafBlock(root.split("/")[3], texture_name, texture_name)

    notint_overrides = jsonData["noTint"]
    block_texture_overrides = jsonData["blockTextures"]
    overlay_textures = jsonData["overlayTextures"]
    overlay_variants = jsonData["overlayVariants"]
    compileonly_textures = jsonData["compileOnly"]
    block_id_overrides = jsonData["blockIds"]
    leaves_with_carpet = jsonData["leavesWithCarpet"]
    dynamictrees_namespaces = jsonData["dynamicTreesNamespaces"]
    generate_itemmodels_overrides = jsonData["generateItemModels"]
    block_state_copies = jsonData["blockStateCopies"]

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

    # We don't want to generate assets for compile-only or overlay textures
    if leaf.getTextureId() in compileonly_textures or leaf.getTextureId() in overlay_textures.values():
        printOverride(f"Skipping {'compile-only' if leaf.getTextureId() in compileonly_textures else 'overlay'} texture")
        return 0

    leaf.use_legacy_model = shouldUseLegacyModel(leaf, root, infile, args)

    # Generate texture
    if not (leaf.use_legacy_model or leaf.getId() in overlay_variants.keys()):
        generateTexture(root, infile, args.programmer)

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
    elif leaf.getId() in overlay_variants:
        leaf.base_model = "leaves_overlay"
        leaf.overlay_texture_id = leaf.getTextureId()
        leaf.texture_id_override = overlay_variants[leaf.getId()]
        printOverride("Has overlay variant: "+leaf.texture_id_override)

    # Check if the block has a dynamic trees addon namespace

    if (leaf.namespace) in dynamictrees_namespaces:
        leaf.dynamictrees_namespace = dynamictrees_namespaces[leaf.namespace]

    # Check if the block should generate an item model
    if leaf.getId() in generate_itemmodels_overrides:
        leaf.should_generate_item_model = True
        printOverride("Also generating item model")

    # Check for blockstate data
    applyJson(leaf, root, infile, files)

    # Generate blockstates & models
    generateBlockstate(leaf, block_state_copies)
    generateBlockModels(leaf)
    generateItemModel(leaf)

    # Certain mods contain leaf carpets.
    # Because we change the leaf texture, we need to fix the carpet models.
    generateCarpet(leaf, leaves_with_carpet)

    return 1

def shouldUseLegacyModel(leaf, root, infile, args) -> bool:
    texture = Image.open(os.path.join(root, infile))
    if texture.size[0] != texture.size[1]:
        printOverride("Animated – using legacy model")
        return True
    if args.legacy:
        printOverride("Using legacy model as requested")
        return True
    return False

def generateCarpet(leaf, leaves_with_carpet):
    if (leaf.getId()) not in leaves_with_carpet: return

    carpet_ids = leaves_with_carpet[leaf.getId()]
    # In case only one carpet is provided (as a string), turn it into a list
    if not isinstance(carpet_ids, list): carpet_ids = [carpet_ids]

    for carpet_id in carpet_ids:
        carpet = CarpetBlock(carpet_id, leaf)
        generateCarpetAssets(carpet)
        printOverride(f"Generating leaf carpet: {carpet.carpet_id}")
