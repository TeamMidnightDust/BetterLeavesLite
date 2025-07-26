import os
from src.json_utils import dumpJson

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

        # Add additional textures
        if (leaf.sprite_overrides):
            for key in leaf.sprite_overrides:
                block_model_data["textures"][key] = leaf.sprite_overrides[key];

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

        item_model_file = f"assets/{mod_namespace}/models/item/{block_name}.json" if (leaf.blockstate_data == None) else f"assets/{leaf.blockstate_data.namespace}/models/item/{leaf.blockstate_data.block_name}.json"
        with open(item_model_file, "w") as f:
            dumpJson(item_model_data, f)
