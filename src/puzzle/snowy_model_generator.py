import os
from src.data.leafblock import LeafBlock
from src.json_utils import dumpJson

def generateSnowyBlockModels(leaf: LeafBlock):
    mod_namespace = leaf.getId().split(":")[0]
    block_name = leaf.getId().split(":")[1]
    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/models/block/".format(mod_namespace), exist_ok=True)

    # Create the four individual leaf models
    for i in range(1, 5):
        # Create structure for block model file
        block_model_file = f"assets/{mod_namespace}/models/block/snowy_{block_name}{i}.json"
        block_model_data = {
            "parent": f"betterleaves:block/leaves_snowy{i}",
            "textures": {
                "all": f"{leaf.getTextureId()}",
                "snowy": f"betterleaves:block/snowy_overlay{leaf.mask_index}"
            }
        }
        # Add overlay texture on request
        if (leaf.overlay_texture_id != ""):
            block_model_data["textures"]["overlay"] = leaf.overlay_texture_id

        # Add additional textures
        if (leaf.sprite_overrides):
            for key in leaf.sprite_overrides:
                block_model_data["textures"][key] = leaf.sprite_overrides[key]

        # Write block model file
        with open(block_model_file, "w") as f:
            dumpJson(block_model_data, f)
