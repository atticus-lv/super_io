<p align="center">
  <a href="https://atticus-lv.gitee.io/super_io/#/">
    <img src="res/img/logo_bg.png" alt="logo" width="540px"/>
  </a>
</p>
<h4 align="center">
    Allow you to copy and paste to import / export models and images. <br>
</h4>
<p align="center">
    Documentation ➡️
    <a href="https://atticus-lv.gitee.io/super_io/#/">
	[Gitee] 
    </a>
    Blender 2.83 ~ 3.0
</p>

# Intro

SPIO is a blender addon that allow you to copy and paste to import or export.

Currently we can not drag and drop to import model in blender, but with this addon, you can easily copy your model/Image
in your File Explorer, then paste in blender with just one click/shortcut,

which has improved the efficiency of importing and exporting blender files / Models / pictures

With third-party Scripts, you are allowed to copy/paste amonng blender, Cinema 4d and Houdini

> Support windows / Mac platforms(Not Fully Support)
>
> (Third Party Scripts Support Cinema4d R23+ and Houdini H18+ on windows)

# Contributing

SPIO needs help from you!

Translation, different platform support, and new features which come from great idea.

# Feature

Check the document above

# Log

> English Log at release panel

### v1.3.5

新

+ c4d spio脚本，现可在c4d与blender之间快速传输模型
+ houdini spio 脚本，现可在houdini与blender之间快速传输模型

UI

+ 改进ui，更加易于使用
+ 将asset helper从实验项移动到单独的偏好选项
+ 减少默认导出器至三个，但可从偏好设置进行扩展

### v1.3.0.3

错误修复

+ 修复mac导入错误
+ 为超级导出添加轮询（防止空选择导出错误）
+ 修复自定义配置导出（win）错误后的打开目录

### v1.3.0.2

错误修复

+ 修复导入菜单
+ 修复菜单错误报告（在某些pc上发生）

### v1.3.0.1

错误修复

+ 覆盖文件将不会推送到剪贴板
+ 导出配置将仅导出导入或导出类型

### v1.3.0

新

+ 用于轻松标记/清除资产的资产帮助器，帮助导出资产混合文件
+ 导出器：blend文件（.blend）

错误修复

+ 修复win导出后打开的目录
+ 修正blend导出器（默认）
+ 修复导出blend打包纹理错误
+ 修复运行多个python时可能的移动文件错误

### v1.2.9

新

+ 现在支持将所有导出文件复制到剪贴板
+ 添加首选项切换：导出后复制到剪贴板（仅限win，mac需要测试）
+ 添加首选项切换：导出后打开导出目录
+ 添加对节点编辑器中UDIM图像检测导入的支持
+ 支持合成器粘贴图像（现在不支持序列）

### v1.2.8

错误修复

+ 修复io类型弹出过滤器
+ 修复mac测试导致的导出错误

本地化

+ 将翻译文件更改为json文件

新

+ 实验功能：插件安装程序

### v1.2.7

+ 实验功能：导出模型/材质资产
+ 修复 gltf 导出器
+ 修复导入菜单中显示的导出配置
+ ui 改进

### v1.2.6

+ 添加检查更新运算符_

### v1.2.5

+ 集成配置系统至 Super Export

### v1.2

+ 一键模型导出 （ctrl shift c），可将选中物体一键导出为（blend/obj/stl/fbx）
    + 导出后复制至剪切板，可一键黏贴到需要的位置，便于发送于整理资产
    + blend文件导出后将打包所有外部引用资产
    + obj/stl/fbx文件支持批量导出功能（按下alt后，每个物体导出为单独文件）
+ 一键图像导出 （ctrl shift c）
    + 图像编辑器中，可选择将图片导出为像素（不支持透明像素）/图像文件，前者可一键黏贴至ps等图像编辑软件

### v1.1.1

+ 修复 2.83~2,.92 自定义配置导入错误

### v1.1

+ 添加对macOS的初步支持
+ 修复兼容2.83所导致的错误
+ 对win平台添加图像编辑器的一键导出功能（不支持透明像素）

### v1.0.1

+ 正式发布