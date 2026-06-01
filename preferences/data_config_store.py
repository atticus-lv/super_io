import json
import os
import re
from pathlib import Path

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup

from .data_config_prop import ConfigItemProperty


ADDON_ID = "super_io"
CONFIG_SCHEMA_VERSION = 2
CONFIG_FILE_NAME = "custom_io_configs.json"
AUTOSAVE_INTERVAL = 0.75
_CONFIG_DIRTY = False
_CONFIG_LOADING = False
_CONFIG_AUTOSAVE_SCHEDULED = False
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
    "bl_idname",
    "context",
    "context_area",
    "show_prop_list",
)
RUNTIME_ONLY_FIELDS = {
    "operator_type",
}
UNSUPPORTED_LEGACY_OPERATORS = {
    "DEFAULT_DAE": "wm.collada_import",
    "DEFAULT_X3D": "import_scene.x3d",
    "EXPORT_DAE": "wm.collada_export",
}
LEGACY_BLEND_TYPES = {
    "APPEND_BLEND_MATERIAL": ("spio.batch_import_blend", {"action": "APPEND", "sub_path": "Material", "data_type": "materials", "load_all": True}),
    "APPEND_BLEND_COLLECTION": ("spio.batch_import_blend", {"action": "APPEND", "sub_path": "Collection", "data_type": "collections", "load_all": True}),
    "APPEND_BLEND_OBJECT": ("spio.batch_import_blend", {"action": "APPEND", "sub_path": "Object", "data_type": "objects", "load_all": True}),
    "APPEND_BLEND_WORLD": ("spio.batch_import_blend", {"action": "APPEND", "sub_path": "World", "data_type": "worlds", "load_all": True}),
    "APPEND_BLEND_NODETREE": ("spio.batch_import_blend", {"action": "APPEND", "sub_path": "NodeTree", "data_type": "node_groups", "load_all": True}),
    "LINK_BLEND_MAT": ("spio.batch_import_blend", {"action": "LINK", "sub_path": "Material", "data_type": "materials", "load_all": True}),
    "LINK_BLEND_COLLECTION": ("spio.batch_import_blend", {"action": "LINK", "sub_path": "Collection", "data_type": "collections", "load_all": True}),
    "LINK_BLEND_OBJECT": ("spio.batch_import_blend", {"action": "LINK", "sub_path": "Object", "data_type": "objects", "load_all": True}),
    "LINK_BLEND_WORLD": ("spio.batch_import_blend", {"action": "LINK", "sub_path": "World", "data_type": "worlds", "load_all": True}),
    "LINK_BLEND_NODE": ("spio.batch_import_blend", {"action": "LINK", "sub_path": "NodeTree", "data_type": "node_groups", "load_all": True}),
}


def is_runtime_config_available():
    return (
        hasattr(bpy.types, "WindowManager")
        and hasattr(bpy.types.WindowManager, "spio_config")
        and hasattr(bpy.context, "window_manager")
        and hasattr(bpy.context.window_manager, "spio_config")
    )


def mark_runtime_config_dirty(_self=None, _context=None):
    global _CONFIG_DIRTY, _CONFIG_AUTOSAVE_SCHEDULED
    if _CONFIG_LOADING or not is_runtime_config_available():
        return

    _CONFIG_DIRTY = True
    if not _CONFIG_AUTOSAVE_SCHEDULED:
        _CONFIG_AUTOSAVE_SCHEDULED = True
        bpy.app.timers.register(_autosave_runtime_config, first_interval=AUTOSAVE_INTERVAL, persistent=True)


def _autosave_runtime_config():
    global _CONFIG_AUTOSAVE_SCHEDULED
    _CONFIG_AUTOSAVE_SCHEDULED = False
    flush_runtime_config_if_dirty()
    return None


def flush_runtime_config_if_dirty(context=None):
    if not _CONFIG_DIRTY or not is_runtime_config_available():
        return None
    return write_runtime_config(context=context)


class ConfigRuntimeProperty(PropertyGroup):
    schema_version: IntProperty(default=CONFIG_SCHEMA_VERSION)
    source_path: StringProperty(name="Config File")
    migrated_from_preferences: BoolProperty(default=False)
    config_list: CollectionProperty(type=ConfigItemProperty)
    config_list_index: IntProperty(min=0, default=0, update=mark_runtime_config_dirty)


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
    config["bl_idname"] = normalize_bl_idname(config.get("bl_idname", ""))

    props = {}
    for prop_item in getattr(item, "prop_list", []):
        if prop_item.name:
            props[prop_item.name] = coerce_json_value(prop_item.value)
    config["prop_list"] = props
    return config


def config_document_from_items(items):
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "addon_id": ADDON_ID,
        "active_index": 0,
        "configs": [serialize_item(item, index) for index, item in enumerate(items)],
    }


def normalize_bl_idname(bl_idname):
    bl_idname = str(bl_idname or "").strip()
    if bl_idname.startswith("bpy.ops."):
        bl_idname = bl_idname[8:]
    if bl_idname.endswith("()"):
        bl_idname = bl_idname[:-2]
    return bl_idname


def is_float(value):
    value = str(value)
    if value.count(".") != 1:
        return False
    left, right = value.split(".")
    return right.isdigit() and (left.isdigit() or (left.startswith("-") and left[1:].isdigit()))


def coerce_json_value(value):
    if not isinstance(value, str):
        return value
    if value in {"True", "False"}:
        return value == "True"
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    if is_float(value):
        return float(value)
    return value


def merge_props(*prop_sets):
    merged = {}
    for props in prop_sets:
        if isinstance(props, dict):
            merged.update(props)
    return merged


def disable_legacy_config(config, operator_type, bl_idname=""):
    config["use_config"] = False
    config["operator_type"] = "CUSTOM"
    config["bl_idname"] = normalize_bl_idname(bl_idname)
    config["context"] = config.get("context") or "EXEC_DEFAULT"
    note = f"Disabled during Blender 5 migration: {operator_type} is not available"
    description = config.get("description", "")
    config["description"] = f"{description}\n{note}".strip()
    return config


def legacy_operator_to_bl_idname(operator_type):
    from ..imexporter.default_addon import importer_addon
    from ..imexporter.default_exporter import get_exporter, get_exporter_ops_props
    from ..imexporter.default_importer import get_importer

    if operator_type in UNSUPPORTED_LEGACY_OPERATORS:
        return UNSUPPORTED_LEGACY_OPERATORS[operator_type], {}, False
    if operator_type.startswith("DEFAULT"):
        ext = operator_type.removeprefix("DEFAULT_").lower()
        bl_idname = get_importer().get(ext)
        return bl_idname, {}, bool(bl_idname)
    if operator_type.startswith("EXPORT"):
        ext = operator_type.removeprefix("EXPORT_").lower()
        bl_idname = get_exporter(extend=True).get(ext)
        return bl_idname, get_exporter_ops_props().get(ext, {}), bool(bl_idname)
    if operator_type in LEGACY_BLEND_TYPES:
        bl_idname, props = LEGACY_BLEND_TYPES[operator_type]
        return bl_idname, props, True
    if operator_type.startswith("ADDONS"):
        bl_idname = importer_addon.get(operator_type)
        return bl_idname, {}, bool(bl_idname)
    if operator_type == "CUSTOM":
        return None, {}, True
    return None, {}, False


def normalize_config(config, index=0):
    config = dict(config)
    if "operator" in config and isinstance(config["operator"], dict):
        operator = config.pop("operator")
        config.setdefault("bl_idname", operator.get("bl_idname", ""))
        config.setdefault("context", operator.get("context", "EXEC_DEFAULT"))
        config.setdefault("context_area", operator.get("area", operator.get("context_area", "VIEW_3D")))
    if "properties" in config and "prop_list" not in config:
        config["prop_list"] = config.pop("properties")

    if not config.get("identifier"):
        config["identifier"] = make_identifier(config.get("name", ""), index)
    config.setdefault("prop_list", {})
    config.setdefault("use_config", True)
    config.setdefault("context", "EXEC_DEFAULT")
    config.setdefault("context_area", "VIEW_3D")
    config.setdefault("show_prop_list", True)
    config.setdefault("operator_type", "CUSTOM")

    operator_type = config.get("operator_type")
    if config.get("bl_idname"):
        config["bl_idname"] = normalize_bl_idname(config["bl_idname"])
        config["operator_type"] = "CUSTOM"
        return config

    if operator_type:
        bl_idname, default_props, supported = legacy_operator_to_bl_idname(operator_type)
        if not supported:
            return disable_legacy_config(config, operator_type, bl_idname or "")
        if bl_idname:
            config["bl_idname"] = normalize_bl_idname(bl_idname)
        config["prop_list"] = merge_props(default_props, config.get("prop_list"))
        config["operator_type"] = "CUSTOM"
    return config


def normalize_document(data):
    if isinstance(data, dict) and "configs" in data:
        configs = data.get("configs") or []
        return {
            "schema_version": CONFIG_SCHEMA_VERSION,
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
        if key in RUNTIME_ONLY_FIELDS and not hasattr(item, key):
            continue
        if hasattr(item, key):
            try:
                setattr(item, key, value)
            except TypeError:
                pass


def default_config_document():
    from ..imexporter.default_exporter import get_exporter, get_exporter_ops_props
    from ..imexporter.default_importer import get_importer

    configs = []
    for ext, bl_idname in get_importer().items():
        configs.append(
            {
                "name": f"Import {ext.upper()}",
                "io_type": "IMPORT",
                "extension": ext,
                "bl_idname": bl_idname,
                "context": "EXEC_DEFAULT",
                "context_area": "VIEW_3D",
                "prop_list": {},
            }
        )

    exporter_props = get_exporter_ops_props()
    for ext, bl_idname in get_exporter(extend=True).items():
        configs.append(
            {
                "name": f"Export {ext.upper()}",
                "io_type": "EXPORT",
                "extension": ext,
                "bl_idname": bl_idname,
                "context": "EXEC_DEFAULT",
                "context_area": "VIEW_3D",
                "prop_list": exporter_props.get(ext, {}),
            }
        )

    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "addon_id": ADDON_ID,
        "active_index": 0,
        "configs": [normalize_config(config, index) for index, config in enumerate(configs)],
    }


def apply_document_to_runtime(data, context=None):
    global _CONFIG_LOADING
    runtime = get_config_data(context)
    _CONFIG_LOADING = True
    try:
        document = normalize_document(data)
        runtime.schema_version = document["schema_version"]
        runtime.config_list.clear()

        for config in document["configs"]:
            item = runtime.config_list.add()
            apply_config_to_item(item, config)

        runtime.source_path = get_config_path(create=True)
        set_config_index(document["active_index"], context)
    finally:
        _CONFIG_LOADING = False
    return runtime


def read_config_file(path=None):
    path = path or get_config_path(create=True)
    with open(path, "r", encoding="utf-8") as f:
        return normalize_document(json.load(f))


def write_runtime_config(path=None, context=None):
    global _CONFIG_DIRTY
    runtime = get_config_data(context)
    path = path or get_config_path(create=True)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    document = config_document_from_items(runtime.config_list)
    document["active_index"] = runtime.config_list_index
    with open(path, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=4, ensure_ascii=False)

    runtime.source_path = path
    _CONFIG_DIRTY = False
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
        legacy_document = {
            "schema_version": 0,
            "addon_id": ADDON_ID,
            "active_index": getattr(pref.preferences, "config_list_index", 0),
            "configs": [serialize_legacy_item(item, index) for index, item in enumerate(pref.preferences.config_list)],
        }
        apply_document_to_runtime(legacy_document, context)
        runtime.migrated_from_preferences = True
        return write_runtime_config(path, context)

    apply_document_to_runtime(default_config_document(), context)
    runtime.migrated_from_preferences = False
    return write_runtime_config(path, context)


def serialize_legacy_item(item, index=0):
    fields = list(CONFIG_ITEM_FIELDS) + ["operator_type"]
    config = {field: getattr(item, field, "") for field in fields if hasattr(item, field)}
    if not config.get("identifier"):
        config["identifier"] = make_identifier(config.get("name", ""), index)
    props = {}
    for prop_item in getattr(item, "prop_list", []):
        if prop_item.name:
            props[prop_item.name] = coerce_json_value(prop_item.value)
    config["prop_list"] = props
    return config


def register():
    bpy.utils.register_class(ConfigRuntimeProperty)
    bpy.types.WindowManager.spio_config = PointerProperty(type=ConfigRuntimeProperty)


def unregister():
    flush_runtime_config_if_dirty()
    del bpy.types.WindowManager.spio_config
    bpy.utils.unregister_class(ConfigRuntimeProperty)
