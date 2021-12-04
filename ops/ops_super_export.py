import bpy
import time
import os
from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from .utils import MeasureTime, ConfigItemHelper, ConfigHelper, PopupImportMenu, PopupExportMenu
from .ops_super_import import import_icon
from .utils import is_float, get_pref, convert_value
from ..ui.icon_utils import RSN_Preview

from ..clipboard.windows import PowerShellClipboard
from ..exporter.default_exporter import default_exporter, exporter_ops_props

export_icon = RSN_Preview(image='export.bip', name='import_icon')


class WM_OT_super_export(bpy.types.Operator):
    """Export to Clipboard"""

    bl_idname = 'wm.super_export'
    bl_label = 'Super Export'

    # dependant class
    #################
    dep_classes = []  # for easier manage, helpful for batch register and un register

    # data
    #################
    clipboard = None  # clipboard data
    file_list = []  # store clipboard urls for importing
    CONFIGS = None  # config list from user preference

    # state
    ###############
    use_custom_config = False  # if there is more then one config that advance user define
    config_list_index: IntProperty()  # index for reading pref config list

    # Utils
    ###########
    def restore(self):
        self.file_list.clear()
        self.clipboard = None
        self.ext = None

    def report_time(self, start_time):
        if get_pref().report_time: self.report({"INFO"},
                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

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
        for index in self.CONFIGS.index_list:
            # only for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)

            # define exec

            def get_temp_dir(self):
                ori_dir = bpy.context.preferences.filepaths.temporary_directory
                temp_dir = ori_dir
                if ori_dir == '':
                    # win temp file
                    temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')

                return temp_dir

            def export_single(self, context, op_callable, op_args):
                paths = []
                temp_dir = self.get_temp_dir()
                filepath = os.path.join(temp_dir, context.active_object.name + f'.{self.extension}')
                paths.append(filepath)

                op_args.update({'filepath': filepath})
                op_callable(**op_args)

                return paths

            def export_batch(self, context, op_callable, op_args):
                paths = []
                temp_dir = self.get_temp_dir()

                src_active = context.active_object
                selected_objects = context.selected_objects.copy()

                for obj in selected_objects:
                    filepath = os.path.join(temp_dir, obj.name + f'.{self.extension}')
                    paths.append(filepath)

                    bpy.ops.object.select_all(action='DESELECT')
                    context.view_layer.objects.active = obj
                    obj.select_set(True)

                    op_args.update({'filepath': filepath})
                    op_callable(**op_args)

                context.view_layer.objects.active = src_active

                return paths

            def invoke(self, context, event):
                self.batch_mode = True if event.alt else False
                return self.execute(context)

            def execute(self, context):
                # use pre-define index to call config
                ITEM = self.ITEM

                op_callable, op_args, op_context = ITEM.get_operator_and_args()

                if op_callable:
                    with MeasureTime() as start_time:
                        if self.batch_mode:
                            paths = self.export_batch(context, op_callable, op_args)
                            self.report({'INFO'},
                                        f'{len(paths)} {self.extension} files has been copied to Clipboard')

                        else:
                            paths = self.export_single(context, op_callable, op_args)
                            self.report({'INFO'},
                                        f'{context.active_object.name}.{self.extension} has been copied to Clipboard')

                        clipboard = PowerShellClipboard()
                        clipboard.push_to_clipboard(paths=paths)

                        if get_pref().report_time: self.report({"INFO"},
                                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
                else:
                    self.report({"ERROR"}, f'{op_callable} Error!!!')

                return {"FINISHED"}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": ITEM.name,
                           "bl_description": ITEM.description,
                           "execute": execute,
                           "invoke": invoke,
                           # custom pass in
                           'ITEM': ITEM,
                           'batch_mode': False,
                           'extension': ITEM.extension,
                           # custom function
                           'export_single': export_single,
                           'export_batch': export_batch,
                           'get_temp_dir': get_temp_dir,
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
            pop = PopupExportMenu(temp_path=None, context=context)
            menu = pop.default_blend_menu(return_menu=True)
            menu(self, context)

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
