from pathlib import Path
from enum import Enum


class ConfigFile(Enum):
    DIRECTORY = '_config.yaml'
    EXPORT_DEFAULT = 'export_default.yaml'
    IMPORT_DEFAULT = 'import_default.yaml'
    IMPORT_SPIO = 'import_spio.yaml'


class AssetDir(Enum):
    DIRECTORY = 'assets'
    ICONS = 'icons'
    IMAGES = 'images'
    SCENES = 'scenes'
    SCRIPTS = 'scripts'
    TEMPLATES = 'templates'


class TemplateDir(Enum):
    WORLD = 'World.blend'
    PARALLAX_MAPPING = 'ParallaxMapping_2022_5_9.blend'


class ScriptDir(Enum):
    pass


class ExternalDir(Enum):
    C4D = 'Super IO for Cinema 4d v0.3'
    HOUDINI = 'Super IO for Houdini v0.4'


class ModulesDir(Enum):
    """Path to modules directory, python files in this directory will be loaded as modules"""
    DIRECTORY = 'modules'


class DefaultIcons(Enum):
    IMPORT = 'import.png'
    EXPORT = 'export.png'


class AssetHelperSceneDir(Enum):
    HDR = 'hdr_scene'
    MATERIAL = 'mat_scene'


class AssetHelperScript(Enum):
    RENDER_MATERIAL_PREVIEW = 'script_render_material_asset_pv.py'
    RENDER_WORLD_PREVIEW = 'script_render_world_asset_pv.py'


def get_modules_dir():
    d = Path(__file__).parent.joinpath(ModulesDir.DIRECTORY.value)

    return d


def get_asset_dir(subpath: AssetDir | None = None) -> Path:
    d = Path(__file__).parent.joinpath(AssetDir.DIRECTORY.value)

    assert subpath is None or isinstance(subpath, AssetDir), f'Asset {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d


def get_template_dir(subpath: TemplateDir | None = None) -> Path:
    d = get_asset_dir().joinpath(AssetDir.TEMPLATES.value)

    assert subpath is None or isinstance(subpath, TemplateDir), f'Template {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d


def get_icon_dir(subpath: DefaultIcons | None = None) -> Path:
    d = get_asset_dir(AssetDir.ICONS)

    assert subpath is None or isinstance(subpath, DefaultIcons), f'Icon {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d


def get_asset_helper_scene_dir(subpath: AssetHelperSceneDir | None = None) -> Path:
    d = get_asset_dir(AssetDir.SCENES).joinpath('asset_helper')

    assert subpath is None or isinstance(subpath, AssetHelperSceneDir), f'Asset helper scene {subpath} not found.'

    if subpath is not None:
        d = d.joinpath(subpath.value)

    return d


def get_asset_helper_script(subpath: AssetHelperScript) -> Path:
    assert isinstance(subpath, AssetHelperScript), f'Asset helper script {subpath} not found.'

    return get_asset_dir(AssetDir.SCRIPTS).joinpath('asset_helper', subpath.value)
