from . import ops_mark_asset, op_resize_image, ops_render_asset_pv, ops_set_preview, ops_snap_shot, op_batch_set, \
    op_pop_editor

classes = (
    ops_mark_asset,
    op_resize_image,
    ops_render_asset_pv,
    ops_set_preview,
    ops_snap_shot,
    op_batch_set,
    op_pop_editor,

)


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in reversed(classes):
        cls.unregister()


if __name__ == '__main__':
    register()
