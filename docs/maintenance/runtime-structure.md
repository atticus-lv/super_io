# Runtime Structure

This page records the intended module boundaries for future maintenance work. The goal is to improve testability and file layout without changing user-facing behavior.

## Current Boundaries

- `__init__.py`: Blender extension entry point. It should stay thin and only coordinate module registration.
- `ops/`: core clipboard import/export operators and shared operator helpers.
- `addon/`: feature modules that extend the main import/export workflow, such as asset helper and addon importers.
- `preferences/`: Blender preference UI, runtime config storage, config item properties, icons, and keymaps.
- `ui/`: panels and menus.
- `imexporter/`: default IO operator mappings, `.blend` helper scripts, and format parser helpers.
- `assets/`: runtime resources, templates, icons, images, and background scripts.
- `third_party_addons/`: release artifacts for external DCC applications. These are not imported by the Blender runtime.

## Target Shape

The preferred long-term layout is domain-first:

- `config/`: config document schema, migration, serialization, and pure validation helpers.
- `operators/`: Blender operator classes grouped by workflow.
- `features/asset_helper/`: asset browser actions, preview rendering, and related menus.
- `features/importers/`: optional import helpers such as PBR zip, IES, addon install, and URL imports.
- `features/exporters/`: optional export helpers.
- `ui/`: panels, menus, and display-only helpers.
- `assets/`: all packaged non-code resources and background scripts.

This target should be reached gradually. Avoid large rename-only commits that make behavior review difficult.

## Migration Rules

- Keep each step covered by `tests/blender/background_smoke.py`.
- Do not save or mutate real user preferences during tests.
- Move pure Python helpers before moving Blender operator classes.
- Preserve public `bl_idname` values and config JSON fields.
- Keep compatibility shims when a module path is likely to be used by user scripts.
- Update path helpers instead of scattering `os.path.dirname(__file__)` lookups.
- Prefer one behavior domain per commit: config, paths, asset helper, import/export, or UI.

## Suggested Order

1. Extract pure config document helpers from `preferences/data_config_store.py` into a testable config module.
2. Move path and resource lookup helpers into a dedicated assets/path module, keeping `public_path_utils.py` as a compatibility layer.
3. Split `ops/core.py` into small modules for config execution, post-processing, and menu building.
4. Move asset helper code out of `addon/asset_helper/` into a domain package after its path usage is fully covered.
5. Move importer/exporter helper operators into domain packages only after smoke tests cover their registration and minimal execution paths.

## Test Expectations

Background Blender tests should remain the main safety net for registration, operator lookup, config migration, PBR material setup, and `.blend` batch append behavior.

Pure Python tests should be added for config normalization, legacy mapping, path helpers, and JSON serialization once those helpers no longer import `bpy`.
