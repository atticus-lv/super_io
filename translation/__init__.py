import bpy
import json
import os
import importlib


class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except(ValueError):
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)


# Set
############
from . import zh_CN

adjt_zh_CN = TranslationHelper('spio_zh_CN', zh_CN.data)
adjt_zh_HANS = TranslationHelper('spio_zh_HANS', zh_CN.data, lang='zh_HANS')


def register():
    if bpy.app.version < (4, 0, 0):
        adjt_zh_CN.register()
    else:
        adjt_zh_HANS.register()
        adjt_zh_CN.register()


def unregister():
    if bpy.app.version < (4, 0, 0):
        adjt_zh_CN.unregister()
    else:
        adjt_zh_HANS.unregister()
        adjt_zh_CN.register()
