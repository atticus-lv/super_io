# 配置数据存储

Super IO 使用带版本号的 JSON 文档保存自定义导入/导出配置。这里说明旧数据结构和当前 Blender 5 数据结构的区别。

## 旧版存储

旧版 Super IO 会把自定义配置存进 Blender 偏好设置。导出的 JSON 也沿用同一套结构，并且很多操作符通过 Super IO 自己的 enum 值来识别。

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

在这个模型里，`operator_type` 是关键字段。`DEFAULT_OBJ`、`EXPORT_STL`、`APPEND_BLEND_MATERIAL` 这类值是 Super IO 自己的标识，运行时再映射到 Blender 操作符。

这会让 Blender API 迁移更麻烦，因为保存的数据同时依赖 Super IO 的 enum 名称和 Blender 的操作符名称。

## 当前存储

现在 Super IO 会在 Blender 偏好设置之外保存一份持久化 JSON 配置文件。文档带有版本号，并且直接使用真实 Blender 操作符 ID 作为执行身份。

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

现在最重要的执行身份是 `bl_idname`，例如 `wm.obj_import`、`wm.stl_export` 或 `spio.batch_import_blend`。显示名称和描述可以变化，但 `bl_idname` 是 Blender 用来执行操作符的 key。

## 数据迁移

Super IO 加载旧数据时，会把旧的 `operator_type` 转成 `bl_idname`：

- `DEFAULT_OBJ` 会变成 `wm.obj_import`。
- `EXPORT_STL` 会变成 `wm.stl_export`。
- `CUSTOM` 会保留原来的 `bl_idname`。
- Blend 追加/链接预设会迁移成 Super IO 的 blend 操作符，并写入必要参数。
- Blender 5 不再支持的旧操作符会被保留但禁用，并在描述中写明原因。

迁移之后，新导出的配置 JSON 会使用 `schema_version: 2`，不再把 `operator_type` 作为保存的执行身份。

## 参数值

`prop_list` 保存传给 Blender 操作符的额外参数。Super IO 会尽量把简单值写成 JSON 原生类型：

```json
{
  "export_selected_objects": true,
  "global_scale": 1.0,
  "path_mode": "AUTO"
}
```

`filepath`、`directory`、文件选择器过滤项这类运行时文件参数由 Super IO 管理，不应该作为普通预设参数保存。
