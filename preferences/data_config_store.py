import json
import os
import re
from pathlib import Path

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup

from ..metadata import ADDON_ID
from .data_config_prop import ConfigItemProperty


CONFIG_SCHEMA_VERSION = 1
CONFIG_FILE_NAME = "custom_io_configs.json"
CONFIG_ITEM_FIELDS = (
    "identifier",
    "use_config",
    "color_tag",
    "io_type",
    "name",
    "description",
    "extension",
    "match_rule",
    "match_value",
    "temporary_directory",
    "operator_type",
    "bl_idname",
    "context",
    "context_area",
    "show_prop_list",
)


class ConfigRuntimeProperty(PropertyGroup):
    schema_version: IntProperty(default=CONFIG_SCHEMA_VERSION)
    source_path: StringProperty(name="Config File")
    migrated_from_preferences: BoolProperty(default=False)
    config_list: CollectionProperty(type=ConfigItemProperty)
    config_list_index: IntProperty(min=0, default=0)


def get_config_data(context=None):
    context = context or bpy.context
    return context.window_manager.spio_config


def get_config_list(context=None):
    return get_config_data(context).config_list


def get_config_index(context=None):
    data = get_config_data(context)
    if len(data.config_list) == 0:
        data.config_list_index = 0
    else:
        data.config_list_index = min(data.config_list_index, len(data.config_list) - 1)
    return data.config_list_index


def set_config_index(index, context=None):
    data = get_config_data(context)
    if len(data.config_list) == 0:
        data.config_list_index = 0
    else:
        data.config_list_index = max(0, min(index, len(data.config_list) - 1))


def get_config_path(create=True):
    root_package = __package__.rsplit(".preferences", 1)[0]
    try:
        base_path = bpy.utils.extension_path_user(root_package, path="", create=create)
    except Exception:
        base_path = bpy.utils.user_resource("CONFIG", path=ADDON_ID, create=create)
    return os.path.join(base_path, CONFIG_FILE_NAME)


def make_identifier(name, index):
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower()).strip("_")
    if not slug:
        slug = "config"
    return f"{slug}_{index + 1:03d}"


def serialize_item(item, index=0):
    config = {field: getattr(item, field, "") for field in CONFIG_ITEM_FIELDS}
    if not config.get("identifier"):
        config["identifier"] = make_identifier(config.get("name", ""), index)

    props = {}
    for prop_item in getattr(item, "prop_list", []):
        if prop_item.name:
            props[prop_item.name] = prop_item.value
    config["prop_list"] = props
    return config


def config_document_from_items(items):
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "addon_id": ADDON_ID,
        "active_index": 0,
        "configs": [serialize_item(item, index) for index, item in enumerate(items)],
    }


def normalize_config(config, index=0):
    config = dict(config)
    if not config.get("identifier"):
        config["identifier"] = make_identifier(config.get("name", ""), index)
    config.setdefault("prop_list", {})
    return config


def normalize_document(data):
    if isinstance(data, dict) and "configs" in data:
        configs = data.get("configs") or []
        return {
            "schema_version": int(data.get("schema_version", CONFIG_SCHEMA_VERSION)),
            "addon_id": data.get("addon_id", ADDON_ID),
            "active_index": int(data.get("active_index", 0) or 0),
            "configs": [normalize_config(config, index) for index, config in enumerate(configs)],
        }

    if isinstance(data, dict):
        configs = []
        for index, (name, config) in enumerate(data.items()):
            if not isinstance(config, dict):
                continue
            migrated = dict(config)
            migrated.setdefault("name", name)
            configs.append(normalize_config(migrated, index))
        return {
            "schema_version": CONFIG_SCHEMA_VERSION,
            "addon_id": ADDON_ID,
            "active_index": 0,
            "configs": configs,
        }

    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "addon_id": ADDON_ID,
        "active_index": 0,
        "configs": [],
    }


def apply_config_to_item(item, config):
    for key, value in normalize_config(config).items():
        if key == "prop_list":
            item.prop_list.clear()
            for prop, prop_value in value.items():
                prop_item = item.prop_list.add()
                prop_item.name = str(prop)
                prop_item.value = str(prop_value)
            continue
        if hasattr(item, key):
            try:
                setattr(item, key, value)
            except TypeError:
                pass


def apply_document_to_runtime(data, context=None):
    runtime = get_config_data(context)
    document = normalize_document(data)
    runtime.schema_version = document["schema_version"]
    runtime.config_list.clear()

    for config in document["configs"]:
        item = runtime.config_list.add()
        apply_config_to_item(item, config)

    runtime.source_path = get_config_path(create=True)
    set_config_index(document["active_index"], context)
    return runtime


def read_config_file(path=None):
    path = path or get_config_path(create=True)
    with open(path, "r", encoding="utf-8") as f:
        return normalize_document(json.load(f))


def write_runtime_config(path=None, context=None):
    runtime = get_config_data(context)
    path = path or get_config_path(create=True)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    document = config_document_from_items(runtime.config_list)
    document["active_index"] = runtime.config_list_index
    with open(path, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=4, ensure_ascii=False)

    runtime.source_path = path
    return path


def load_or_migrate_runtime_config(context=None):
    runtime = get_config_data(context)
    path = get_config_path(create=True)

    if os.path.exists(path):
        apply_document_to_runtime(read_config_file(path), context)
        runtime.migrated_from_preferences = False
        return path

    pref = bpy.context.preferences.addons.get(__package__.rsplit(".preferences", 1)[0])
    if pref and getattr(pref.preferences, "config_list", None):
        legacy_document = config_document_from_items(pref.preferences.config_list)
        apply_document_to_runtime(legacy_document, context)
        runtime.migrated_from_preferences = True
        return write_runtime_config(path, context)

    apply_document_to_runtime({}, context)
    runtime.migrated_from_preferences = False
    return write_runtime_config(path, context)


def register():
    bpy.utils.register_class(ConfigRuntimeProperty)
    bpy.types.WindowManager.spio_config = PointerProperty(type=ConfigRuntimeProperty)


def unregister():
    del bpy.types.WindowManager.spio_config
    bpy.utils.unregister_class(ConfigRuntimeProperty)
