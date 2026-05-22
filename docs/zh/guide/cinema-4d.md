# Cinema 4D 插件

Super IO 内置了一个 Cinema 4D 插件，用来配合 Blender 侧的剪贴板导入导出流程。

<div class="spio-shot">
  <img src="/media/img/readme/f_addon.png" alt="第三方插件面板">
</div>

## 要求

- Cinema 4D R23 或更新版本。
- 已在 Blender 中安装并启用打包发布版 Super IO。

## 安装

1. 在 Blender 中打开 `Edit > Preferences > Add-ons` 或 `Edit > Preferences > Extensions`。
2. 打开 Super IO 的偏好设置。
3. 在 `Third-party` 区域点击 `Install Cinema 4d Plugin`。
4. 点击 `Install Tutorial` 打开随包插件目录。
5. 将 `Super IO for Cinema 4d v0.2` 复制到 Cinema 4D 的 `plugins` 目录。
6. 重启 Cinema 4D。

安装后，可以在 Cinema 4D 的扩展菜单中找到 Super IO 命令。

## Blender 侧

Cinema 4D 插件只是流程的一端。Blender 里仍然需要启用 Super IO，并使用正常的导入导出快捷键。

<div class="spio-shot">
  <img src="/media/img/readme/f_preset.png" alt="Super IO 导入预设">
</div>

## 排查

如果 Cinema 4D 中没有显示插件，请确认插件文件夹已经复制到当前 Cinema 4D 使用的 `plugins` 目录，并在复制后重启 Cinema 4D。

如果 Blender 没有收到粘贴的文件，请确认 Super IO 已启用，并且剪贴板中的内容是受支持的文件路径或剪贴板格式。
