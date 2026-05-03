# Older Blender Versions

Super IO 2.x requires Blender 5.0 or newer.

If you use Blender 4.x, 3.x, or 2.8x, install an older Super IO release from the [GitHub Releases page](https://github.com/atticus-lv/super_io/releases).

## Why The Split Exists

Blender 5 uses the new extension format and has different import/export operator APIs. Super IO 2.x drops old compatibility branches so the current code can focus on Blender 5 behavior.

## Upgrade Checklist

Before upgrading from an older Super IO version:

1. Export your custom import/export config if possible.
2. Install the Blender 5 extension package from GitHub Releases.
3. Start Blender and let Super IO migrate old custom data when possible.
4. Check your custom operators, especially ones that target old Blender import/export operators.
