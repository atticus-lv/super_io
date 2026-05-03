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

from super_io.preferences.data_config_store import get_config_data  # noqa: E402


config_data = get_config_data()
config_data.config_list.clear()

item = config_data.config_list.add()
item.name = "Smoke OBJ Import"
item.extension = "obj"
item.operator_type = "DEFAULT_OBJ"
item.io_type = "IMPORT"
prop = item.prop_list.add()
prop.name = "use_split_objects"
prop.value = "True"

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
            }
        },
        indent=4,
    ),
    encoding="utf-8",
)

result = bpy.ops.spio.import_config(filepath=str(old_json))
assert result == {"FINISHED"}, result
assert any(config.name == "Legacy FBX Import" for config in config_data.config_list)

result = bpy.ops.spio.export_config(filepath=str(new_json), export_all=True)
assert result == {"FINISHED"}, result

exported = json.loads(new_json.read_text(encoding="utf-8"))
assert exported["schema_version"] == 1
assert exported["addon_id"] == "super_io"
assert isinstance(exported["configs"], list)
assert any(config["name"] == "Smoke OBJ Import" for config in exported["configs"])
assert any(config["name"] == "Legacy FBX Import" for config in exported["configs"])

super_io.unregister()
print("SPIO_SMOKE_OK")
