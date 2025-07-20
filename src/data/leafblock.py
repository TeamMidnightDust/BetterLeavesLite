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
    sprite_overrides = None

    def getId(self):
        if (self.block_id_override != None): return self.block_id_override
        return self.namespace+":"+self.block_name

    def getTextureId(self):
        if (self.texture_id_override != None): return self.texture_id_override
        return self.namespace+":block/"+self.texture_prefix+self.texture_name
