# 旧版 Blender

Super IO 2.x 要求 Blender 5.0 或更新版本。

如果你使用 Blender 4.x、3.x 或 2.8x，请从 [GitHub Releases](https://github.com/atticus-lv/super_io/releases) 下载旧版 Super IO。

## 为什么拆分版本

Blender 5 使用新的扩展格式，并且部分导入导出操作符 API 已经变化。Super IO 2.x 放弃旧版兼容分支后，可以更专注地维护 Blender 5 行为。

## 升级检查

从旧版 Super IO 升级前，建议：

1. 尽可能先导出自定义导入/导出配置。
2. 从 GitHub Releases 安装 Blender 5 扩展包。
3. 启动 Blender，让 Super IO 尽可能迁移旧自定义数据。
4. 检查自定义操作符，尤其是指向旧版 Blender 导入导出操作符的配置。
