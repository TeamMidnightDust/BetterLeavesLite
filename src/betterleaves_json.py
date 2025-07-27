import json
import os
from src.data.leafblock import LeafBlock
from src.data.blockstate_data import BlockStateData

def applyJson(leaf: LeafBlock, root, infile, files):
    if infile.replace(".png", ".betterleaves.json") in files:
        with open(os.path.join(root, infile.replace(".png", ".betterleaves.json")), "r") as f:
            jsonFile = json.load(f)
            if "blockStateData" in jsonFile:
                leaf.blockstate_data = BlockStateData.fromFile(leaf, root, infile.replace(".png", ".betterleaves.json"))
            if "spriteOverrides" in jsonFile:
                leaf.sprite_overrides = jsonFile["spriteOverrides"]
