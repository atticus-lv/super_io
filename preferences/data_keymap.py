import bpy
import sys

addon_keymaps = []


def add_keymap_item(km, idname, key, value, **modifiers):
    kmi = km.keymap_items.new(idname, key, value, **modifiers)
    addon_keymaps.append((km, kmi))

    if sys.platform == 'darwin' and modifiers.get('ctrl'):
        oskey_modifiers = modifiers.copy()
        oskey_modifiers['ctrl'] = False
        oskey_modifiers['oskey'] = True
        kmi = km.keymap_items.new(idname, key, value, **oskey_modifiers)
        addon_keymaps.append((km, kmi))


def register():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        add_keymap_item(km, "wm.super_import", 'V', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        add_keymap_item(km, "wm.super_import", 'V', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        add_keymap_item(km, "wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='Image Generic', space_type='IMAGE_EDITOR')
        add_keymap_item(km, "wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        add_keymap_item(km, "wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
        add_keymap_item(km, "wm.super_import", 'V', 'PRESS', ctrl=True, shift=True)

        km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
        add_keymap_item(km, "wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)


def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()
