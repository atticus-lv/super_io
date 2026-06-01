# Third-party Addons

This directory contains companion plugins for other DCC applications. They are release artifacts, not part of the Blender extension runtime.

## Contents

- `Super IO for Cinema 4d v0.3/`: Cinema 4D plugin files copied by the Blender extension.
- `Super IO for Houdini v0.4/`: Houdini package, shelf, icons, and scripts copied or referenced by the Blender extension.

## Maintenance Boundary

- Keep these folders self-contained. Do not import code from them into the Blender extension package.
- Treat plugin folder names as release-facing identifiers. If a versioned folder name changes, update:
  - `.github/workflows/third-party-plugins.yml`
  - Blender operators that copy or open third-party plugin folders
  - user documentation under `docs/guide/`
- The main Blender CI does not execute Cinema 4D or Houdini APIs. Changes here should be reviewed with manual testing in the target DCC application.
- Generated files such as `__pycache__` and `.pyc` files must not be committed.

## Packaging

The `Third-Party Plugins` workflow packages these folders only for tag builds:

- `super_io-cinema4d-v0.3.zip`
- `super_io-houdini-v0.4.zip`

The archive root preserves the folder under `third_party_addons/`, so install documentation can refer to the same folder names users see in the release assets.

## Update Checklist

1. Update the plugin folder contents.
2. Keep the folder version and workflow package name in sync.
3. Confirm the Blender-side install/copy operator still points at the right folder.
4. Manually test import/export through the target DCC application.
5. Update `docs/guide/cinema-4d.md` or `docs/guide/houdini.md` when install steps or supported versions change.
