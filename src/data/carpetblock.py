class CarpetBlock:
    def __init__(self, carpet_id, leaf):
        self.carpet_id = carpet_id
        self.leaf = leaf
        if (leaf.has_no_tint): self.base_model = "leaf_carpet_notint"

    base_model = "leaf_carpet"
