import os
import json

from src.data.leafblock import LeafBlock
from src.utilities import printOverride

class BlockStateData:
    def __init__(self, namespace, block_name, state):
        self.namespace = namespace
        self.block_name = block_name
        self.state = state

    @classmethod # https://stackoverflow.com/a/682545
    def fromJson(cls, leaf: LeafBlock, data):
        return cls(data["block"].split(":")[0], data["block"].split(":")[1], data["state"]) if "block" in data else cls(leaf.getId().split(":")[0], leaf.getId().split(":")[1], data["state"])

    @classmethod
    def fromFile(cls, leaf: LeafBlock, root, infile):
        with open(os.path.join(root, infile), "r") as f:
            printOverride("Loading blockstate data from: "+f.name)
            return BlockStateData.fromJson(leaf, json.load(f).get("blockStateData"))
