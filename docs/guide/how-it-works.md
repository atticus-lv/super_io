# How It Works

Super IO builds paste and copy menus from the current clipboard data, the active Blender editor, and the user's custom configuration.

## Import Flow

Only one file extension group is processed in a single import action. This keeps the generated menu predictable and avoids mixing incompatible operators.

When no custom config is available, Super IO falls back to the default behavior:

- Blend files open a blend import menu.
- Known model formats use Blender's default import operators.
- Unknown files are treated as image-like inputs when possible.

When custom configs exist for an extension:

- A config without a match rule can be used directly.
- A config with a matching filename rule can be used directly.
- Non-matching files are delayed and passed to the fallback menu after matching imports finish.

## Persistent Configuration

Super IO 2.x stores custom import/export data in a versioned JSON file and loads it into Blender's `WindowManager` at registration time. This keeps runtime access fast while making future data migrations easier.

Old preference-based custom data is still migrated when possible.

## Default Operators

Blender 5 changed several import/export operator names. Super IO 2.x uses Blender 5 operators such as `wm.obj_import`, `wm.stl_import`, `wm.ply_import`, `wm.fbx_import`, and their matching export operators where available.
