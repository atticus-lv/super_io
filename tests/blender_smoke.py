import json
import sys
from pathlib import Path


def _arg_value(name, default=None):
    if "--" not in sys.argv:
        return default
    args = sys.argv[sys.argv.index("--") + 1:]
    if name not in args:
        return default
    index = args.index(name)
    return args[index + 1]


workspace = Path(_arg_value("--workspace", ".")).resolve()
package_parent = workspace.parent
sys.path.insert(0, str(package_parent))

import bpy  # noqa: E402
import super_io  # noqa: E402


super_io.register()

from super_io.preferences.data_config_store import get_config_data, normalize_document, serialize_legacy_item  # noqa: E402
from super_io.preferences.operator_inspector import get_operator_label, iter_operator_properties, operator_exists  # noqa: E402
from super_io.imexporter.default_importer import get_importer  # noqa: E402
from super_io.imexporter.default_exporter import get_exporter, get_exporter_ops_props  # noqa: E402
from super_io.ops.core import ConfigItemHelper  # noqa: E402


def assert_operator_exists(bl_idname):
    op = getattr(getattr(bpy.ops, bl_idname.split(".")[0]), bl_idname.split(".")[1])
    op.get_rna_type()


for bl_idname in {
    *get_importer().values(),
    *get_exporter(extend=True).values(),
}:
    assert_operator_exists(bl_idname)

assert get_importer()["obj"] == "wm.obj_import"
assert get_importer()["stl"] == "wm.stl_import"
assert get_importer()["ply"] == "wm.ply_import"
assert get_importer()["fbx"] == "wm.fbx_import"
assert get_exporter()["obj"] == "wm.obj_export"
assert get_exporter()["stl"] == "wm.stl_export"
assert get_exporter(extend=True)["ply"] == "wm.ply_export"
assert get_exporter_ops_props()["obj"] == {"export_selected_objects": True}
assert_operator_exists("bpy.ops.image.clipboard_paste".removeprefix("bpy.ops."))
assert_operator_exists("object.empty_image_add")
assert_operator_exists("image.import_as_mesh_planes")
assert operator_exists("wm.obj_import")
assert get_operator_label("wm.obj_import") != "wm.obj_import"
assert any(prop["identifier"] == "use_split_objects" for prop in iter_operator_properties("wm.obj_import"))


config_data = get_config_data()
assert config_data.schema_version == 2
assert any(config.bl_idname == "wm.obj_import" for config in config_data.config_list)
assert any(config.bl_idname == "wm.obj_export" for config in config_data.config_list)
config_data.config_list.clear()

item = config_data.config_list.add()
item.name = "Smoke OBJ Import"
item.extension = "obj"
item.bl_idname = "wm.obj_import"
item.io_type = "IMPORT"
prop = item.prop_list.add()
prop.name = "use_split_objects"
prop.value = "True"

helper = ConfigItemHelper(item)
op_callable, op_args, op_context = helper.get_operator_and_args()
assert op_callable.get_rna_type().bl_rna.identifier == bpy.ops.wm.obj_import.get_rna_type().bl_rna.identifier
assert op_args == {"use_split_objects": True}
assert op_context == "EXEC_DEFAULT"

legacy_pref_item = config_data.config_list.add()
legacy_pref_item.name = "Legacy Preference OBJ"
legacy_pref_item.extension = "obj"
legacy_pref_item.operator_type = "DEFAULT_OBJ"
legacy_pref_item.io_type = "IMPORT"
legacy_pref_document = normalize_document(
    {
        "schema_version": 0,
        "configs": [serialize_legacy_item(legacy_pref_item)],
    }
)
assert legacy_pref_document["configs"][0]["bl_idname"] == "wm.obj_import"
config_data.config_list.remove(len(config_data.config_list) - 1)

old_json = workspace / "build" / "smoke_old_config.json"
new_json = workspace / "build" / "smoke_new_config.json"
old_json.parent.mkdir(parents=True, exist_ok=True)
old_json.write_text(
    json.dumps(
        {
            "Legacy FBX Import": {
                "name": "Legacy FBX Import",
                "extension": "fbx",
                "operator_type": "DEFAULT_FBX",
                "io_type": "IMPORT",
                "prop_list": {"automatic_bone_orientation": True},
            },
            "Legacy STL Export": {
                "name": "Legacy STL Export",
                "extension": "stl",
                "operator_type": "EXPORT_STL",
                "io_type": "EXPORT",
                "prop_list": {},
            },
            "Legacy Custom Import": {
                "name": "Legacy Custom Import",
                "extension": "obj",
                "operator_type": "CUSTOM",
                "bl_idname": "wm.obj_import",
                "io_type": "IMPORT",
                "prop_list": {"use_split_groups": False},
            },
            "Legacy Append Material": {
                "name": "Legacy Append Material",
                "extension": "blend",
                "operator_type": "APPEND_BLEND_MATERIAL",
                "io_type": "IMPORT",
                "prop_list": {},
            },
            "Legacy DAE Import": {
                "name": "Legacy DAE Import",
                "extension": "dae",
                "operator_type": "DEFAULT_DAE",
                "io_type": "IMPORT",
                "prop_list": {},
            },
            "Legacy X3D Import": {
                "name": "Legacy X3D Import",
                "extension": "x3d",
                "operator_type": "DEFAULT_X3D",
                "io_type": "IMPORT",
                "prop_list": {},
            },
            "Legacy DAE Export": {
                "name": "Legacy DAE Export",
                "extension": "dae",
                "operator_type": "EXPORT_DAE",
                "io_type": "EXPORT",
                "prop_list": {},
            }
        },
        indent=4,
    ),
    encoding="utf-8",
)

result = bpy.ops.spio.import_config(filepath=str(old_json))
assert result == {"FINISHED"}, result
legacy_fbx = next(config for config in config_data.config_list if config.name == "Legacy FBX Import")
assert legacy_fbx.bl_idname == "wm.fbx_import"
assert legacy_fbx.operator_type == "CUSTOM"
legacy_stl = next(config for config in config_data.config_list if config.name == "Legacy STL Export")
assert legacy_stl.bl_idname == "wm.stl_export"
assert {prop.name: prop.value for prop in legacy_stl.prop_list} == {"export_selected_objects": "True"}
legacy_custom = next(config for config in config_data.config_list if config.name == "Legacy Custom Import")
assert legacy_custom.bl_idname == "wm.obj_import"
assert {prop.name: prop.value for prop in legacy_custom.prop_list} == {"use_split_groups": "False"}
legacy_append = next(config for config in config_data.config_list if config.name == "Legacy Append Material")
assert legacy_append.bl_idname == "spio.batch_import_blend"
assert {prop.name: prop.value for prop in legacy_append.prop_list} == {
    "action": "APPEND",
    "sub_path": "Material",
    "data_type": "materials",
    "load_all": "True",
}
legacy_dae = next(config for config in config_data.config_list if config.name == "Legacy DAE Import")
assert legacy_dae.use_config is False
assert legacy_dae.operator_type == "CUSTOM"
assert legacy_dae.bl_idname == "wm.collada_import"
legacy_x3d = next(config for config in config_data.config_list if config.name == "Legacy X3D Import")
assert legacy_x3d.use_config is False
assert legacy_x3d.bl_idname == "import_scene.x3d"
legacy_dae_export = next(config for config in config_data.config_list if config.name == "Legacy DAE Export")
assert legacy_dae_export.use_config is False
assert legacy_dae_export.bl_idname == "wm.collada_export"

result = bpy.ops.spio.export_config(filepath=str(new_json), export_all=True)
assert result == {"FINISHED"}, result

exported = json.loads(new_json.read_text(encoding="utf-8"))
assert exported["schema_version"] == 2
assert exported["addon_id"] == "super_io"
assert isinstance(exported["configs"], list)
smoke_export = next(config for config in exported["configs"] if config["name"] == "Smoke OBJ Import")
assert smoke_export["bl_idname"] == "wm.obj_import"
assert "operator_type" not in smoke_export
assert smoke_export["prop_list"] == {"use_split_objects": True}
assert any(config["name"] == "Legacy FBX Import" and config["bl_idname"] == "wm.fbx_import" for config in exported["configs"])

super_io.unregister()
print("SPIO_SMOKE_OK")
