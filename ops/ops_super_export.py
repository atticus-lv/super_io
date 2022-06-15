import bpy

from .dynamic_io import IO_Base
from .core import MeasureTime, ConfigItemHelper, ConfigHelper
from .core import is_float, get_pref, convert_value

from ..preferences.data_icon import G_ICON_ID


class WM_OT_super_export(IO_Base, bpy.types.Operator):
    """Export to Clipboard"""
    bl_idname = 'wm.super_export'
    bl_label = 'Super Export'

    def invoke(self, context, event):
        self.restore()
        # filter user's configs
        self.CONFIGS = ConfigHelper(check_use=True, io_type='EXPORT')

        self.use_custom_config = not self.CONFIGS.is_empty()

        return self.export_custom_dynamic(context)

    def export_custom_dynamic(self, context):
        # unregister_class
        self.unregister_dep_classes()
        self.dep_classes.clear()

        # dynamic operator
        ##################
        from .dynamic_io import DynamicExport

        if self.use_custom_config:

            for index in self.CONFIGS.index_list:
                # pass in
                config_item = get_pref().config_list[index]
                ITEM = ConfigItemHelper(config_item)
                if not ITEM.is_config_item_poll(context.area.type): continue

                op_cls = type("DynOp",
                              (bpy.types.Operator,),
                              {"bl_idname": f'wm.spio_config_{index}',
                               "bl_label": ITEM.name,
                               "bl_description": ITEM.description,
                               "execute": DynamicExport.execute,
                               "invoke": DynamicExport.invoke,
                               "poll": DynamicExport.poll,
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
            self.register_dep_classes()

        ############################
        # pop up menu
        ############################

        export_op = self

        def draw_custom_menu(self, context):
            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            # import default popmenu
            from .core import PopupExportMenu
            pop = PopupExportMenu(temp_path=None, context=context)
            menu = None

            if context.area.type == 'VIEW_3D':
                if len(export_op.dep_classes) > 0:
                    for cls in export_op.dep_classes:
                        layout.operator(cls.bl_idname)

                layout.separator()
                menu = pop.default_blend_menu(return_menu=True)

            elif context.area.type == "IMAGE_EDITOR":
                menu = pop.default_image_menu(return_menu=True)

            elif context.area.type == 'FILE_BROWSER' and context.area.ui_type == 'ASSETS':
                menu = pop.default_assets_menu(return_menu=True)

            elif context.area.type == 'NODE_EDITOR':
                menu = pop.default_node_editor_menu(return_menu=True)

            # draw menu
            if menu: menu(self, context)

        context.window_manager.popup_menu(draw_custom_menu, title="Super Export", icon='FILEBROWSER')

        return {'FINISHED'}


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.super_export', icon_value=G_ICON_ID['export'])


def register():
    bpy.utils.register_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.remove(draw_menu)
