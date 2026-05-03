# 自定义配置

自定义配置可以把复制的文件路由到指定 Blender 操作符，并传入指定参数。

## 添加配置

打开 Super IO 偏好设置，添加一个自定义导入/导出项。一个配置通常包含：

- 名称和提示文本，用于显示在 Super IO 菜单中。
- 文件扩展名，例如 `obj`、`blend` 或 `png`。
- IO 类型：导入或导出。
- 操作符类型或自定义操作符 ID。
- 可选的操作符参数。
- 可选的文件名匹配规则，例如前缀、后缀或其它支持的规则。

<div class="spio-shot">
  <img src="/media/img/cn/0.png" alt="自定义配置字段">
</div>

## 导入和导出 JSON 配置

Super IO 可以把自定义配置导出为 JSON，也可以稍后再导入。

在 Super IO 2.x 中，这个 JSON 格式带有版本号。扩展也会在 Blender 偏好设置之外保存一份持久化 JSON 配置文件，以便后续数据迁移。

<div class="spio-shot">
  <img src="/media/img/cn/2.png" alt="配置导入导出按钮">
</div>

## 搜索和匹配

配置列表可以按名称、扩展名、规则、颜色标签和 IO 类型过滤。

<div class="spio-shot">
  <img src="/media/img/cn/3.png" alt="配置搜索过滤器">
</div>

## 示例：blend 材质导入

假设文件名是 `M_IamMaterial.blend`，你可以创建一个识别材质 blend 文件的预设：

1. 添加新配置。
2. 扩展名设为 `blend`。
3. 匹配规则设为前缀。
4. 匹配值设为 `M_`。
5. 操作符类型设为追加材质。

这样以 `M_` 开头的文件就可以直接使用材质导入预设，而不必每次从所有 blend 导入选项里选择。
