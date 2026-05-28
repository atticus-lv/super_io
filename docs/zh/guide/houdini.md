# Houdini 工具架

Super IO 内置了一个 Houdini 工具架，用来通过剪贴板在 Houdini 和 Blender 之间传递模型文件。

<div class="spio-shot">
  <img src="/media/img/readme/f_addon.png" alt="第三方插件面板">
</div>

## 要求

- Houdini 18 或更新版本，并使用 Python 3。
- 随包 Houdini 剪贴板脚本当前面向 Windows。
- 已在 Blender 中安装并启用打包发布版 Super IO。

Houdini 工具可以从剪贴板导入 `obj`、`fbx`、`stl`、`dae`、`abc`、`usd`、`usda` 和 `usdc` 文件。

## 从 Blender 安装

1. 在 Blender 中打开 `Edit > Preferences > Add-ons` 或 `Edit > Preferences > Extensions`。
2. 打开 Super IO 的偏好设置。
3. 在 `Third-party` 区域点击 `Install Houdini Package`。
4. 选择对应的 Houdini 版本。
5. 确认 `Packages Path`，通常是 `Documents/houdini{version}/packages`。
6. 点击 `Install`。

Super IO 会写入一个 `SPIO.json` 包配置文件，让 Houdini 指向随包的 `Super IO for Houdini v0.4` 目录。

## 在 Houdini 添加工具架

1. 打开 Houdini。
2. 点击工具架区域的 `+`。
3. 找到 `SPIO` 并添加到工具架。
4. 分别给 `Super import` 和 `Super export` 绑定快捷键。

快捷键是必须的。Houdini 脚本会读取鼠标所在的 Network Editor 来判断应该在哪个网络中创建或修改节点。

## 使用 Super Import

1. 从 Blender 导出或复制受支持的文件。
2. 在 Houdini 中，把鼠标移动到 SOP level 的 Network Editor 上。
3. 按下 `Super import` 快捷键。

如果没有选中节点，Super IO 会在当前网络里创建 file、Alembic 或 USD 导入节点。如果选中了一个兼容节点，Super IO 会先填充该节点的文件路径，再为剩余文件创建节点。

## 使用 Super Export

1. 在 Houdini 中选中要导出的 SOP 节点。
2. 把鼠标移动到 Network Editor 上。
3. 按下 `Super export` 快捷键。
4. 在 Blender 中粘贴或导入导出的文件。

<div class="spio-shot">
  <img src="/media/img/readme/f_config.png" alt="Super IO 配置面板">
</div>

## 排查

### `NoneType` object has no attribute `pwd`

这通常表示直接点击了 shelf tool，或者执行快捷键时鼠标不在 Houdini 的 Network Editor 上。

把鼠标移动到 SOP Network Editor 上，再通过绑定好的快捷键触发 `Super import` 或 `Super export`。

### No Files Found

请确认剪贴板里包含文件路径，并且文件扩展名在支持范围内。
