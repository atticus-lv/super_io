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
        self.preview_collections["spio_icon"] = pcoll

    def unregister(self):
        for pcoll in self.preview_collections.values():
            previews.remove(pcoll)
        self.preview_collections.clear()

    def get_image(self):
        return self.preview_collections["spio_icon"][self.name]

    def get_image_icon_id(self):
        image = self.get_image()
        return image.icon_id


import os


def t3dn_bip_convert_batch(dir, ext='png'):
    dir = dir.replace('\\', '/')
    dir = dir + '/' if dir[-1] != '/' else dir  # 补全文件夹路径用于cmd cd
    # 获取原始文件夹下名字并设置新路径 （名字不带空格）
    src_lst = [file for file in os.listdir(dir) if file.endswith('.' + ext)]
    tgz_lst = [file.removesuffix('.' + ext) + '.bip' for file in src_lst]
    # 转换
    for i, file_name in enumerate(src_lst):
        os.system(f'cd {dir} & python -m t3dn_bip_converter {src_lst[i]} {tgz_lst[i]}')


def t3dn_bip_convert(src, tgz):
    dir = os.path.dirname(src)
    dir = dir.replace('\\', '/')
    os.system(f'cd {dir} & python -m t3dn_bip_converter {src} {tgz}')
