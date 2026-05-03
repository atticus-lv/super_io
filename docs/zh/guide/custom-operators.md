# 自定义操作符

当内置预设不够用时，可以让 Super IO 调用指定的 Blender 操作符。

## 操作符 ID

大多数 Blender 按钮都能复制到对应的 Python 操作符：

1. 鼠标悬停在 Blender 的操作按钮上。
2. 右键复制 Python 命令。
3. 粘贴到 Super IO 的自定义操作符字段。
4. 如有需要，移除参数和括号，只保留操作符 ID。

例如 `bpy.ops.wm.obj_import()` 会变成 `wm.obj_import`。

## 执行上下文

Super IO 可以用不同执行模式调用操作符：

- `EXEC_DEFAULT` 会直接执行操作符，适合可重复使用的预设。
- `INVOKE_DEFAULT` 会让 Blender 显示操作符自身的弹窗，前提是该操作符支持。

导入文件时，Super IO 会通过该操作符支持的文件参数传入路径，通常是 `filepath` 或 `files`。

## 参数

自定义配置可以定义额外的操作符参数。它适合保存布尔值、字符串、数字，或 Blender 导入导出器里的稳定选项。
