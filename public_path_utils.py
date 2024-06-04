from pathlib import Path
import os
from enum import Enum
import re


class ConfigFile(Enum):
    DIRECTORY = '_config.yaml'
    EXPORT_DEFAULT = 'export_default.yaml'
    IMPORT_DEFAULT = 'import_default.yaml'
    IMPORT_SPIO = 'import_spio.yaml'


class AssetDir(Enum):
    DIRECTORY = 'asset'
    SCRIPTS = 'scripts'
    TEMPLATES = 'templates'


class TemplateDir(Enum):
    WORLD = 'World.blend'
    PARALLAX_MAPPING = 'ParallaxMapping_2022_5_9.blend'


class ScriptDir(Enum):
    pass


class ExternalDir(Enum):
    C4D = 'Super IO for Cinema 4d v0.2'
    HOUDINI = 'Super IO for Houdini v0.3'


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


def get_asset_dir(subpath: AssetDir | None = None) -> Path:
    d = Path(__file__).parent.joinpath(AssetDir.DIRECTORY.value)

    assert subpath in AssetDir or subpath is None, f'Asset {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d


def get_template_dir(subpath: TemplateDir | None = None) -> Path:
    d = get_asset_dir().joinpath(AssetDir.TEMPLATES.value)

    assert subpath in TemplateDir or subpath is None, f'Template {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d
