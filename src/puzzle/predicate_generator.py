import os
from src.json_utils import dumpJson

def generatePredicates(leaf):
    mod_namespace = leaf.getId().split(":")[0]
    block_name = leaf.getId().split(":")[1]
    # Create models folder if it doesn't exist already
    os.makedirs("assets/{}/mbp/".format(mod_namespace), exist_ok=True)

    # Create structure for block model file
    predicate_definition_file = f"assets/{mod_namespace}/mbp/{block_name}.json"
    predicate_definition_data = {
        "overrides": [
            {
                "when": {
                    "or": [
                      {
                        "adjacent_block": {
                            "state": "minecraft:snow",
                            "offset": { "x": 0, "y": 1, "z": 0 }
                        }
                      },
                      {
                        "adjacent_block": {
                            "state": "minecraft:snow_block",
                            "offset": { "x": 0, "y": 1, "z": 0 }
                        }
                      }
                    ]
                },
                "apply": [
                    f"{mod_namespace}:snowy_{block_name}1",
                    f"{mod_namespace}:snowy_{block_name}2",
                    f"{mod_namespace}:snowy_{block_name}3",
                    f"{mod_namespace}:snowy_{block_name}4"
                ]
            }
        ]
    }

    # Write predicate file
    with open(predicate_definition_file, "w") as f:
        dumpJson(predicate_definition_data, f)
