# 快速开始

Super IO 2.x 是面向 Blender 5.0+ 的剪贴板导入导出扩展。

## 安装

1. 从 [GitHub Releases](https://github.com/atticus-lv/super_io/releases) 下载打包好的 `super_io-*.zip`。
2. 把 zip 文件拖进 Blender 窗口。
3. Blender 询问如何处理文件时，点击 `Install`。
4. 安装完成后启用 Super IO。

不要直接安装 GitHub 的源码 zip。Blender 扩展需要使用发布页里的打包 zip。

## 从剪贴板导入

1. 在资源管理器或 Finder 中复制一个或多个文件。
2. 回到 Blender，切换到 3D 视图、着色器编辑器、几何节点编辑器或图像编辑器等支持的上下文。
3. 按 `Ctrl+Shift+V`。
4. 如果 Super IO 弹出菜单，选择需要的导入方式。

Super IO 可以根据当前上下文导入模型、blend 文件、图片、SVG 和文件夹。

## 导出到剪贴板

1. 在 3D 视图中选择对象，或在图像编辑器中打开图片。
2. 按 `Ctrl+Shift+C`。
3. 选择导出方式。
4. 在文件管理器或其它应用里粘贴导出的文件。

## Blender 4.x 及更早版本

最新 Super IO 只支持 Blender 5.0+。如果你使用旧版 Blender，请从 [发布历史](https://github.com/atticus-lv/super_io/releases) 下载旧版本插件。
