---
layout: home

hero:
  name: Super IO
  text: Clipboard-driven import and export for Blender 5
  tagline: Copy files in your file manager, paste them into Blender, and keep custom IO rules under versioned JSON configuration.
  image:
    src: /media/logo/logo_bg.png
    alt: Super IO logo
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: Download Release
      link: https://github.com/atticus-lv/super_io/releases

features:
  - title: Blender 5 Extension
    details: Super IO 2.x is packaged as a Blender extension and requires Blender 5.0 or newer.
  - title: Clipboard First
    details: Import files with Ctrl+Shift+V and export selected objects with Ctrl+Shift+C.
  - title: Custom IO Rules
    details: Route formats, filenames, and operators through a versioned JSON-backed configuration system.
---

<div class="spio-strip">
  <div class="spio-strip__item">
    <div class="spio-strip__label">Import</div>
    <p>Copy model, blend, SVG, image, or folder paths and paste them into the active Blender context.</p>
  </div>
  <div class="spio-strip__item">
    <div class="spio-strip__label">Export</div>
    <p>Export selected models or images and place the result back on the system clipboard.</p>
  </div>
  <div class="spio-strip__item">
    <div class="spio-strip__label">Customize</div>
    <p>Match by extension, name rule, and operator type when the default import/export flow is not enough.</p>
  </div>
</div>

<div class="spio-shot">
  <img src="/media/img/cn/img.png" alt="Super IO import menu">
</div>

Super IO is designed for short, repeated IO tasks: moving files from Explorer or Finder into Blender, exporting selected assets back to the file system, and using custom presets when a file type needs special treatment.

For Blender 4.x and earlier, use an older package from the [release history](https://github.com/atticus-lv/super_io/releases).
