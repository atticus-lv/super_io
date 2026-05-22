# Houdini Shelf Tool

Super IO includes a Houdini shelf tool for sending model files between Houdini and Blender through the clipboard workflow.

<div class="spio-shot">
  <img src="/media/img/readme/f_addon.png" alt="Third-party addon panel">
</div>

## Requirements

- Houdini 18 or newer with Python 3.
- Windows for the bundled Houdini clipboard scripts.
- A packaged Super IO release installed and enabled in Blender.

The bundled Houdini tool can import `obj`, `fbx`, `stl`, `dae`, `abc`, `usd`, `usda`, and `usdc` files from the clipboard.

## Install From Blender

1. In Blender, open `Edit > Preferences > Add-ons` or `Edit > Preferences > Extensions`.
2. Open the Super IO preferences.
3. In `Third-party`, click `Install Houdini Package`.
4. Pick the matching Houdini version.
5. Confirm the `Packages Path`, usually `Documents/houdini{version}/packages`.
6. Click `Install`.

Super IO writes an `SPIO.json` package file that points Houdini to the bundled `Super IO for Houdini v0.3` folder.

## Add The Shelf In Houdini

1. Open Houdini.
2. Click the `+` button on the shelf area.
3. Find `SPIO` and add it to the shelf.
4. Assign shortcuts to both `Super import` and `Super export`.

The shortcuts are required. The Houdini scripts use the Network Editor under the mouse cursor to decide where to create or edit nodes.

## Use Super Import

1. Export or copy supported files from Blender.
2. In Houdini, move the mouse over the Network Editor at SOP level.
3. Press the `Super import` shortcut.

If no node is selected, Super IO creates file, Alembic, or USD import nodes in the current network. If one compatible node is selected, Super IO fills that node's file path first, then creates nodes for any remaining files.

## Use Super Export

1. In Houdini, select the SOP node you want to export.
2. Move the mouse over the Network Editor.
3. Press the `Super export` shortcut.
4. Paste or import the exported file in Blender.

<div class="spio-shot">
  <img src="/media/img/readme/f_config.png" alt="Super IO configuration panel">
</div>

## Troubleshooting

### `NoneType` object has no attribute `pwd`

This usually means the shelf tool was clicked directly, or the mouse was not over Houdini's Network Editor when the shortcut ran.

Move the mouse over the SOP Network Editor and trigger `Super import` or `Super export` with the assigned shortcut.

### No Files Found

Confirm that the clipboard contains file paths and that the files use a supported extension.
