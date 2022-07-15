import bpy
import os
import sys
import time

from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from .core import get_pref, MeasureTime, PostProcess


class IO_Base(bpy.types.Operator):
    """IO template"""

    # dependant class
    #################
    dep_classes = []  # for easier manage, helpful for batch register and un register

    # data
    #################
    clipboard = None  # clipboard data
    file_list = []  # store file urls for importing
    dir_list = []  # store directory urls for importing
    CONFIGS = None  # config list from user preference

    # state
    ###############
    use_custom_config = False  # if there is more then one config that advance user define
    config_list_index: IntProperty()  # index for reading pref config list

    # Utils
    ###########
    def restore(self):
        self.dir_list.clear()
        self.file_list.clear()
        self.clipboard = None
        self.ext = None
        self.use_custom_config = False

    def register_dep_classes(self):
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

    def unregister_dep_classes(self):
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)

    def report_time(self, start_time):
        if get_pref().report_time: self.report({"INFO"},
                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

    # Import Method
    def import_blend_default(self, context):
        """Import with default popup"""
        pass

    def import_default(self, context):
        """Import with blender's default setting"""
        pass

    # Import Method (Popup)
    ##############
    def import_custom_dynamic(self, context):
        pass

    # Export Method (Popup)
    ##############
    def export_custom_dynamic(self, context):
        pass


class DynamicImport:
    # define exec
    def execute(self, context):
        # use pre-define index to call config
        ITEM = self.ITEM

        op_callable, ops_args, op_context = ITEM.get_operator_and_args()

        if op_callable:
            with MeasureTime() as start_time:
                for file_path in self.file_list:
                    if file_path in self.match_file_op_dict: continue
                    ops_args['filepath'] = file_path
                    try:
                        if op_context:
                            op_callable(op_context, **ops_args)
                        else:
                            op_callable(**ops_args)
                    except Exception as e:
                        self.report({"ERROR"}, str(e))

                if get_pref().report_time: self.report({"INFO"},
                                                       f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        else:
            self.report({"ERROR"}, f'{op_callable} Error!!!')

        return {"FINISHED"}


class DynamicExport:

    @classmethod
    def poll(self, context):
        return context.active_object is not None and len(context.selected_objects) != 0

    def get_temp_dir(self):
        temp_dir = self.ITEM.temporary_directory
        if temp_dir == '':
            temp_dir = bpy.path.abspath(bpy.context.preferences.filepaths.temporary_directory)
            if temp_dir == '':
                # win temp file
                temp_dir = os.path.join(os.path.expanduser('~'), 'spio_temp')
                if not "spio_temp" in os.listdir(os.path.expanduser('~')):
                    os.makedirs(temp_dir)
        else:
            temp_dir = bpy.path.abspath(temp_dir)
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

        return temp_dir

    def export_single(self, context, op_callable, op_args):
        paths = []
        temp_dir = self.get_temp_dir()
        filepath = os.path.join(temp_dir, context.active_object.name + f'.{self.extension}').replace('\\', '/')
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
            filepath = os.path.join(temp_dir, obj.name + f'.{self.extension}').replace('\\', '/')
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
            temp_dir = self.get_temp_dir()
            # set dict for checking overwrite obj time
            src_file = dict()
            for file in os.listdir(temp_dir):
                src_file[file] = os.path.getmtime(os.path.join(temp_dir, file))

            with MeasureTime() as start_time:
                if self.batch_mode:
                    paths = self.export_batch(context, op_callable, op_args)
                    self.report({'INFO'},
                                f'{len(paths)} {self.extension} files has been copied to Clipboard')

                else:
                    paths = self.export_single(context, op_callable, op_args)
                    self.report({'INFO'},
                                f'{context.active_object.name}.{self.extension} has been copied to Clipboard')

                # Pref
                POST = PostProcess()
                POST.copy_to_clipboard(paths=PostProcess.get_update_files(src_file, temp_dir), op=self)
                POST.open_dir(temp_dir)

                if get_pref().report_time: self.report({"INFO"},
                                                       f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        else:
            self.report({"ERROR"}, f'{op_callable} Error!!!')

        return {"FINISHED"}
