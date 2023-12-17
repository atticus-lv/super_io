from pathlib import Path
import os
from enum import Enum
import re


class ConfigFile(Enum):
    DIRECTORY = '_config.yaml'
    EXPORT_DEFAULT = 'export_default.yaml'
    IMPORT_DEFAULT = 'import_default.yaml'
    IMPORT_SPIO = 'import_spio.yaml'


class ScriptDir(Enum):
    pass


class ExternalDir(Enum):
    C4D = 'Super IO for Cinema 4d v0.2'
    HOUDINI = 'Super IO for Houdini v0.3'


class AssetDir(Enum):
    CATEGORY_DEFINE = 'blender_assets.cats.txt'
    MODIFIER = 'modifier'
    MESHLESS_PATTERN = 'meshless_pattern'
    LIGHTING = 'lighting'


class ModulesDir(Enum):
    """Path to modules directory, python files in this directory will be loaded as modules"""
    DIRECTORY = 'modules'


class DefaultIcons(Enum):
    IMPORT = 'import.png'
    EXPORT = 'export.png'

    IMPORT_BIP = 'import_.bip'
    EXPORT_BIP = 'export.bip'

def get_modules_dir():
    d = Path(__file__).parent.joinpath(ModulesDir.DIRECTORY.value)

    return d