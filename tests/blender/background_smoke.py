import base64
import json
import os
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


def _assert_inside(path, root):
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise AssertionError(f"{path} is outside isolated test runtime {root}") from exc


def _write_png(path):
    path.write_bytes(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
        )
    )


workspace = Path(_arg_value("--workspace", ".")).resolve()
runtime_dir = Path(_arg_value("--runtime-dir", workspace / "build" / "blender-test-runtime")).resolve()
config_dir = Path(_arg_value("--config-dir", runtime_dir / "super_io_config")).resolve()
runtime_dir.mkdir(parents=True, exist_ok=True)
config_dir.mkdir(parents=True, exist_ok=True)

os.environ["SPIO_CONFIG_DIR"] = str(config_dir)
(config_dir / "custom_io_configs.json").unlink(missing_ok=True)

package_parent = workspace.parent
sys.path.insert(0, str(package_parent))

import bpy  # noqa: E402
import super_io  # noqa: E402
from super_io.ops import op_image_io  # noqa: E402
from super_io.ops.ops_super_import import SuperImport, get_remaining_import_files  # noqa: E402


super_io.register()

from super_io.imexporter.default_exporter import get_exporter, get_exporter_ops_props  # noqa: E402
from super_io.imexporter.default_importer import get_importer  # noqa: E402
from super_io.ops.core import ConfigItemHelper  # noqa: E402
from super_io.preferences.data_config_store import (  # noqa: E402
    flush_runtime_config_if_dirty,
    get_config_data,
    get_config_path,
    normalize_document,
    save_runtime_config_before_file_load,
    serialize_legacy_item,
)
from super_io.preferences.operator_inspector import get_operator_label, iter_operator_properties, operator_exists  # noqa: E402


class _PrincipledTags:
    displacement = "disp displacement"
    base_color = "basecolor base color albedo diffuse diff"
    sss_color = "sss subsurface"
    metallic = "metal metallic metalness"
    specular = "specular spec"
    rough = "rough roughness"
    gloss = "gloss glossy"
    normal = "normal nor nrm"
    bump = "bump"
    transmission = "transmission"
    emission = "emission emit"
    alpha = "alpha opacity"
    ambient_occlusion = "ao ambient occlusion"


class _SmokePreferences:
    principled_tags = _PrincipledTags()


def _get_smoke_preferences():
    return _SmokePreferences()


def assert_operator_exists(bl_idname):
    op = getattr(getattr(bpy.ops, bl_idname.split(".")[0]), bl_idname.split(".")[1])
    op.get_rna_type()


def smoke_default_operator_maps():
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


def smoke_operator_inspector():
    assert operator_exists("wm.obj_import")
    assert get_operator_label("wm.obj_import") != "wm.obj_import"
    assert any(prop["identifier"] == "use_split_objects" for prop in iter_operator_properties("wm.obj_import"))


def smoke_config_io():
    config_path = Path(get_config_path()).resolve()
    _assert_inside(config_path, runtime_dir)

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

    item.description = "Autosave smoke check"
    autosave_path = Path(flush_runtime_config_if_dirty()).resolve()
    _assert_inside(autosave_path, runtime_dir)
    autosaved = json.loads(autosave_path.read_text(encoding="utf-8"))
    autosaved_smoke = next(config for config in autosaved["configs"] if config["name"] == "Smoke OBJ Import")
    assert autosaved_smoke["description"] == "Autosave smoke check"
    assert config_path == autosave_path

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

    old_json = workspace / "tests" / "fixtures" / "configs" / "legacy_v0_config.json"
    new_json = runtime_dir / "outputs" / "smoke_new_config.json"
    new_json.parent.mkdir(parents=True, exist_ok=True)

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


def smoke_config_reload_after_file_load():
    assert any(
        getattr(handler, "__name__", "") == "save_runtime_config_before_file_load"
        for handler in bpy.app.handlers.load_pre
    )
    assert any(
        getattr(handler, "__name__", "") == "load_runtime_config_after_file_load"
        for handler in bpy.app.handlers.load_post
    )

    config_data = get_config_data()
    config_data.config_list.clear()
    item = config_data.config_list.add()
    item.name = "Smoke Reload OBJ Import"
    item.extension = "obj"
    item.bl_idname = "wm.obj_import"
    item.io_type = "IMPORT"

    save_runtime_config_before_file_load(None)
    result = bpy.ops.wm.read_homefile(use_empty=True)
    assert result == {"FINISHED"}, result

    config_data = get_config_data()
    assert any(config.name == "Smoke Reload OBJ Import" for config in config_data.config_list)


def smoke_import_image_as_nodes_assigns_image():
    texture_dir = runtime_dir / "textures" / "ClipboardNode"
    texture_dir.mkdir(parents=True, exist_ok=True)
    image_path = texture_dir / "ClipboardPaste.png"
    _write_png(image_path)

    material = bpy.data.materials.new("SmokeClipboardNodeMaterial")
    material.use_nodes = True

    class _FakeArea:
        type = "NODE_EDITOR"
        ui_type = "ShaderNodeTree"

    class _FakeSpace:
        node_tree = material.node_tree
        edit_tree = material.node_tree
        shader_type = "OBJECT"
        cursor_location = (0, 0)

    class _FakeContext:
        area = _FakeArea()
        space_data = _FakeSpace()

    class _FakeOperator:
        files = str(image_path)
        load_image_by_path = op_image_io.image_io.load_image_by_path

        def report(self, report_type, message):
            raise AssertionError(f"{report_type}: {message}")

    result = op_image_io.SPIO_OT_import_image_as_nodes.execute(_FakeOperator(), _FakeContext())
    assert result == {"FINISHED"}, result

    image_nodes = [
        node
        for node in material.node_tree.nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image is not None
    ]
    assert image_nodes
    assert any(Path(bpy.path.abspath(node.image.filepath)).resolve() == image_path.resolve() for node in image_nodes)


def smoke_custom_import_match_rules():
    config_data = get_config_data()
    source_material = bpy.data.materials.new("SmokeRuleMatchedMaterial")
    source_blend = runtime_dir / "blend" / "RuleMatched.blend"
    source_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.data.libraries.write(str(source_blend), {source_material}, fake_user=True)
    bpy.data.materials.remove(source_material)
    assert bpy.data.materials.get("SmokeRuleMatchedMaterial") is None

    item = config_data.config_list.add()
    config_index = len(config_data.config_list) - 1
    item.name = "Smoke Blend Rule Import"
    item.extension = "blend"
    item.bl_idname = "spio.batch_import_blend"
    item.io_type = "IMPORT"
    item.match_rule = "ENDSWITH"
    item.match_value = "RuleMatched"
    for name, value in {
        "action": "APPEND",
        "data_type": "materials",
        "load_all": "True",
    }.items():
        prop = item.prop_list.add()
        prop.name = name
        prop.value = value

    assert get_remaining_import_files(
        [str(source_blend), str(source_blend.with_suffix(".png"))],
        {str(source_blend): item},
        "blend",
    ) == [str(source_blend.with_suffix(".png"))]

    class _FakeImport:
        file_list = [str(source_blend)]
        dir_list = []
        dep_classes = []
        ext = "blend"

        class _Configs:
            index_list = [config_index]

        CONFIGS = _Configs()

        def register_dep_classes(self):
            for cls in self.dep_classes:
                bpy.utils.register_class(cls)

        def unregister_dep_classes(self):
            for cls in self.dep_classes:
                bpy.utils.unregister_class(cls)

        def report(self, report_type, message):
            raise AssertionError(f"{report_type}: {message}")

        def report_time(self, _start_time):
            pass

    class _FakeContext:
        window_manager = bpy.context.window_manager

        class area:
            type = "VIEW_3D"

    try:
        result = SuperImport.import_custom_dynamic(_FakeImport(), _FakeContext())
        assert result == {"FINISHED"}, result
        assert bpy.data.materials.get("SmokeRuleMatchedMaterial") is not None
    finally:
        config_data.config_list.remove(config_index)


def smoke_pbr_material_setup():
    op_image_io.get_pref = _get_smoke_preferences

    texture_dir = runtime_dir / "textures" / "SmokeMaterial"
    texture_dir.mkdir(parents=True, exist_ok=True)
    for name in ("SmokeMaterial_basecolor.png", "SmokeMaterial_roughness.png", "SmokeMaterial_normal.png"):
        _write_png(texture_dir / name)

    result = bpy.ops.spio.create_principled_set_up_material(
        directory=f"{texture_dir}/",
        use_context_space=False,
        mark_asset=True,
    )
    assert result == {"FINISHED"}, result

    material = bpy.data.materials.get("SmokeMaterial")
    assert material is not None
    assert material.asset_data is not None
    image_nodes = [node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeTexImage"]
    assert len(image_nodes) >= 2


def smoke_batch_append_blend():
    material = bpy.data.materials.new("SmokeAppendMaterial")
    source_blend = runtime_dir / "blend" / "append_source.blend"
    source_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.data.libraries.write(str(source_blend), {material}, fake_user=True)
    bpy.data.materials.remove(material)
    assert bpy.data.materials.get("SmokeAppendMaterial") is None

    result = bpy.ops.spio.batch_import_blend(
        action="APPEND",
        files=str(source_blend),
        data_type="materials",
        load_all=True,
    )
    assert result == {"FINISHED"}, result
    assert bpy.data.materials.get("SmokeAppendMaterial") is not None


def main():
    try:
        smoke_default_operator_maps()
        smoke_operator_inspector()
        smoke_config_io()
        smoke_config_reload_after_file_load()
        smoke_import_image_as_nodes_assigns_image()
        smoke_custom_import_match_rules()
        smoke_pbr_material_setup()
        smoke_batch_append_blend()
    finally:
        super_io.unregister()

    print("SPIO_BACKGROUND_SMOKE_OK")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
