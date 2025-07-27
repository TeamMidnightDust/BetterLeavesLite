import os
import json

from src.json_utils import dumpJson
from src.utilities import printOverride

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
            if state not in block_state_data["variants"]: block_state_data["variants"][state] = []

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
