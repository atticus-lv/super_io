import bpy


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
import os
import json

dir = os.path.dirname(__file__)
help_classes = []

for file in os.listdir(dir):
    if not file.endswith('.json'): continue
    with open(os.path.join(dir, file), 'r', encoding='utf-8') as f:
        d = json.load(f)
        help_cls = TranslationHelper('spio_' + file, d)
        help_classes.append(help_cls)


def register():
    for cls in help_classes:
        cls.register()


def unregister():
    for cls in help_classes:
        cls.unregister()
