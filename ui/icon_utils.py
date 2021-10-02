import os
import bpy
from .t3dn_bip import previews

icons_dir = os.path.join(os.path.dirname(__file__), "icons")

class RSN_Preview():
    def __init__(self, image, name):
        self.preview_collections = {}
        self.image = os.path.join(icons_dir, image)
        self.name = name

    def register(self):
        pcoll = previews.new()
        pcoll.load(self.name, self.image, 'IMAGE')
        self.preview_collections["rsn_icon"] = pcoll

    def unregister(self):
        for pcoll in self.preview_collections.values():
            previews.remove(pcoll)
        self.preview_collections.clear()

    def get_image(self):
        return self.preview_collections["rsn_icon"][self.name]

    def get_image_icon_id(self):
        image = self.get_image()
        return image.icon_id