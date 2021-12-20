import bpy

from .op_dynamic_io import IO_Base
from .core import MeasureTime, ConfigItemHelper, ConfigHelper
from .core import is_float, get_pref, convert_value
from ..ui.icon_utils import RSN_Preview

export_icon = RSN_Preview(image='export.bip', name='import_icon')


class WM_OT_super_export(IO_Base, bpy.types.Operator):
    """Export to Clipboard"""

    bl_idname = 'wm.super_export'
    bl_label = 'Super Export'

    def invoke(self, context, event):
        self.restore()

        self.CONFIGS = ConfigHelper(check_use=True, io_type='EXPORT')
        config_list, index_list = self.CONFIGS.config_list, self.CONFIGS.index_list

        if self.CONFIGS.is_empty():
            self.use_custom_config = False
            return self.execute(context)

        self.use_custom_config = True
        # set default index to prevent default index is not in the filter list ui

        self.config_list_index = index_list[0]
        return self.export_custom_dynamic(context)

    def execute(self, context):
        if self.use_custom_config is False:
            from .core import PopupExportMenu
            popup = PopupExportMenu(temp_path=None, context=context)

            if context.area.type == "VIEW_3D":
                popup.default_blend_menu()
            elif context.area.type == "IMAGE_EDITOR":
                popup.default_image_menu()

        return {'FINISHED'}

    def export_custom_dynamic(self, context):
        # unregister_class
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)
        self.dep_classes.clear()

        # dynamic operator
        ##################
        from .op_dynamic_io import DynamicExport

        for index in self.CONFIGS.index_list:
            # pass in
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": ITEM.name,
                           "bl_description": ITEM.description,
                           "execute": DynamicExport.execute,
                           "invoke": DynamicExport.invoke,
                           # custom pass in
                           'ITEM': ITEM,
                           'batch_mode': False,
                           'extension': ITEM.extension,
                           # custom function
                           'export_single': DynamicExport.export_single,
                           'export_batch': DynamicExport.export_batch,
                           'get_temp_dir': DynamicExport.get_temp_dir,
                           },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        ############################
        # execute
        ############################

        export_op = self

        def draw_custom_menu(self, context):
            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            if len(export_op.dep_classes) > 0:
                for cls in export_op.dep_classes:
                    layout.operator(cls.bl_idname)

            layout.separator()

            # default popup
            from .core import PopupExportMenu
            pop = PopupExportMenu(temp_path=None, context=context)
            menu = None

            if context.area.type == "IMAGE_EDITOR":
                menu = pop.default_image_menu(return_menu=True)
            elif context.area.type == 'VIEW_3D':
                menu = pop.default_blend_menu(return_menu=True)

            if menu: menu(self, context)

        context.window_manager.popup_menu(draw_custom_menu, title="Super Export", icon='FILEBROWSER')

        return {'FINISHED'}


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.super_export', icon_value=export_icon.get_image_icon_id())


def register():
    export_icon.register()

    bpy.utils.register_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.append(draw_menu)


def unregister():
    export_icon.unregister()

    bpy.utils.unregister_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.remove(draw_menu)
