# Config Storage

Super IO stores custom import/export configs in a versioned JSON document. This page explains the old storage model and the current Blender 5 storage model.

## Old Storage

Older Super IO versions stored custom configs in Blender preferences. Exported JSON used the same shape and identified many operators through Super IO enum values.

```json
{
  "OBJ Import": {
    "name": "OBJ Import",
    "extension": "obj",
    "io_type": "IMPORT",
    "operator_type": "DEFAULT_OBJ",
    "prop_list": {
      "use_split_objects": true
    }
  }
}
```

In that model, `operator_type` was the important field. Values like `DEFAULT_OBJ`, `EXPORT_STL`, or `APPEND_BLEND_MATERIAL` were Super IO identifiers. Super IO then mapped those identifiers to Blender operators at runtime.

This made Blender API updates harder because the saved data depended on both Super IO enum names and Blender operator names.

## Current Storage

Super IO now stores configs outside Blender preferences in a persistent JSON file. The document is versioned and uses real Blender operator identifiers as the execution identity.

```json
{
  "schema_version": 2,
  "addon_id": "super_io",
  "active_index": 0,
  "configs": [
    {
      "identifier": "obj_import_001",
      "use_config": true,
      "io_type": "IMPORT",
      "name": "OBJ Import",
      "description": "",
      "extension": "obj",
      "match_rule": "NONE",
      "match_value": "",
      "temporary_directory": "",
      "bl_idname": "wm.obj_import",
      "context": "EXEC_DEFAULT",
      "context_area": "VIEW_3D",
      "show_prop_list": true,
      "prop_list": {
        "use_split_objects": true
      }
    }
  ]
}
```

The main identity is now `bl_idname`, such as `wm.obj_import`, `wm.stl_export`, or `spio.batch_import_blend`. Display names and descriptions can change, but `bl_idname` is the Blender operator key used for execution.

## Migration

When Super IO loads old data, it converts legacy `operator_type` values into `bl_idname`:

- `DEFAULT_OBJ` becomes `wm.obj_import`.
- `EXPORT_STL` becomes `wm.stl_export`.
- `CUSTOM` keeps the saved `bl_idname`.
- Blend append/link presets become Super IO blend operators with the needed properties.
- Unsupported Blender 5 operators are kept but disabled, with a note in the description.

After migration, newly exported config JSON uses `schema_version: 2` and does not use `operator_type` as the saved execution identity.

## Property Values

`prop_list` stores extra arguments passed to the Blender operator. Super IO writes simple values as typed JSON where possible:

```json
{
  "export_selected_objects": true,
  "global_scale": 1.0,
  "path_mode": "AUTO"
}
```

Runtime file arguments such as `filepath`, `directory`, and file selector filters are managed by Super IO and should not be stored as normal preset properties.
