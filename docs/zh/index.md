---
layout: home

hero:
  name: Super IO
  text: 面向 Blender 5 的剪贴板导入导出扩展
  tagline: 在文件管理器里复制文件，在 Blender 里粘贴导入；选中对象后一键导出，并用版本化 JSON 管理自定义规则。
  image:
    src: /media/logo/logo_bg.png
    alt: Super IO 标志
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/guide/getting-started
    - theme: alt
      text: 下载发布包
      link: https://github.com/atticus-lv/super_io/releases

features:
  - title: Blender 5 扩展
    details: Super IO 2.x 已迁移为 Blender Extension，并要求 Blender 5.0 或更新版本。
  - title: 剪贴板优先
    details: 使用 Ctrl+Shift+V 导入复制的文件，使用 Ctrl+Shift+C 导出选中对象。
  - title: 自定义导入导出规则
    details: 按格式、文件名规则和操作符类型决定具体导入导出方式。
---

<div class="spio-strip">
  <div class="spio-strip__item">
    <div class="spio-strip__label">导入</div>
    <p>复制模型、blend、SVG、图片或文件夹路径，然后在 Blender 对应上下文里粘贴。</p>
  </div>
  <div class="spio-strip__item">
    <div class="spio-strip__label">导出</div>
    <p>导出选中模型或图片，并把生成的文件放回系统剪贴板。</p>
  </div>
  <div class="spio-strip__item">
    <div class="spio-strip__label">自定义</div>
    <p>默认流程不够用时，可以通过扩展名、匹配规则和操作符配置专用预设。</p>
  </div>
</div>

<div class="spio-shot">
  <img src="/media/img/cn/img.png" alt="Super IO 导入菜单">
</div>

Super IO 适合高频、重复的导入导出动作：把资源管理器里的文件带入 Blender，把选中的资产导出到文件系统，并在特殊格式需要特殊处理时使用自定义配置。

如果你仍在使用 Blender 4.x 或更早版本，请从 [旧版本发布页](https://github.com/atticus-lv/super_io/releases) 下载对应的旧插件包。
