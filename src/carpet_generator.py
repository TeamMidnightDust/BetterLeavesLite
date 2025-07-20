import os
from src.json_utils import dumpJson

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
