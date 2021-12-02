import bpy
from .. import __folder_name__
from bpy.props import CollectionProperty

import time
import os


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


def viewlayer_fix_291(self, context):
    return context.view_layer.depsgraph if bpy.app.version >= (2, 91, 0) else context.view_layer


class MeasureTime():
    def __enter__(self):
        return time.time()

    def __exit__(self, type, value, traceback):
        pass


def is_float(s) -> bool:
    s = str(s)
    if s.count('.') == 1:
        left, right = s.split('.')  # [1,1]#-s.2
        if left.isdigit() and right.isdigit():
            return True
        elif left.startswith('-') and left.count('-') == 1 \
                and left[1:].isdigit() and right.isdigit():
            return True

    return False


def convert_value(value):
    if value.isdigit():
        return int(value)
    elif is_float(value):
        return float(value)
    elif value in {'True', 'False'}:
        return eval(value)
    else:
        return value


from ..loader.default_importer import default_importer
from ..loader.default_blend import default_blend_lib
from ..loader.addon_blend import addon_blend


class ConfigItemHelper():
    def __init__(self, item):
        self.item = item
        for key in item.__annotations__.keys():
            value = getattr(item, key)
            if key != 'prop_list':
                self.__setattr__(key, value)
            # prop list
            ops_config = dict()
            if len(item.prop_list) != 0:
                for prop_index, prop_item in enumerate(item.prop_list):
                    prop, value = prop_item.name, prop_item.value
                    # skip if the prop is not filled
                    if prop == '' or value == '': continue
                    ops_config[prop] = convert_value(value)
            self.__setattr__('prop_list', ops_config)

    def get_operator_and_args(self):
        op_callable = None
        ops_args = dict()
        operator_type = self.operator_type
        op_context = None

        # custom operator
        if operator_type == 'CUSTOM':
            # custom operator
            bl_idname = self.bl_idname
            op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
            ops_args = self.prop_list
            op_context = self.context

        # default operator
        elif operator_type.startswith('DEFAULT'):
            if bpy.app.version < (3, 0, 0):
                bl_idname = default_exporter.get(operator_type.removeprefix('DEFAULT_').lower())
            else:
                bl_idname = default_exporter.get(operator_type[8:].lower())
            op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

        elif operator_type.startswith('APPEND_BLEND'):
            if bpy.app.version < (3, 0, 0):
                subpath = operator_type.removeprefix('APPEND_BLEND_').title()
            else:
                subpath = operator_type[13:].title()

            data_type = default_blend_lib.get(subpath)
            op_callable = bpy.ops.spio.append_blend
            ops_args = {'sub_path': subpath,
                        'data_type': data_type,
                        'load_all': True}

        elif operator_type.startswith('LINK_BLEND'):
            subpath = operator_type.removeprefix('LINK_BLEND_').title()
            data_type = default_blend_lib.get(subpath)
            op_callable = bpy.ops.spio.link_blend
            ops_args = {'sub_path': subpath,
                        'data_type': data_type,
                        'load_all': True}

        elif operator_type.startswith('ADDONS'):
            bl_idname = addon_blend.get(operator_type)
            op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

        return op_callable, ops_args, op_context

    def get_match_files(self, file_list):
        match_rule = self.match_rule
        match_value = self.match_value

        if match_rule == 'NONE':
            match_files = list()
        elif match_rule == 'STARTSWITH':
            match_files = [file for file in file_list if os.path.basename(file).startswith(match_value)]
        elif match_rule == 'ENDSWITH':
            match_files = [file for file in file_list if
                           os.path.basename(file).removesuffix('.' + self.ext).endswith(match_value)]
        elif match_rule == 'IN':
            match_files = [file for file in file_list if match_value in os.path.basename(file)]
        elif match_rule == 'REGEX':
            import re
            match_files = [file for file in file_list if re.search(match_value, os.path.basename(file))]

        return match_files


class ConfigHelper():
    def __init__(self, check_use=False, filter=None):
        pref_config = get_pref().config_list

        config_list = dict()
        index_list = []

        for config_list_index, item in enumerate(pref_config):
            # config dict
            config = dict()
            # get define property
            for key in item.__annotations__.keys():
                value = getattr(item, key)
                if key != 'prop_list':
                    config[key] = value
                # prop list
                ops_config = dict()
                if len(item.prop_list) != 0:
                    for prop_index, prop_item in enumerate(item.prop_list):
                        prop, value = prop_item.name, prop_item.value
                        # skip if the prop is not filled
                        if prop == '' or value == '': continue
                        ops_config[prop] = convert_value(value)
                config['prop_list'] = ops_config

            # check config dict
            if True in (config.get('name') == '',
                        config.get('operator_type') == 'CUSTOM' and config.get('bl_idname') == '',
                        config.get('extension') == '',
                        filter and config.get('extension') != filter,
                        check_use and config.get('use_config') is False,
                        ): continue

            index_list.append(config_list_index)
            config_list[item.name] = config

        self.config_list = config_list
        self.index_list = index_list

    def get_prop_list_from_index(self, index):
        if index > len(self.config_list) - 1: return None

        config_item = self.config_list[index]
        return config_item.get('prop_list')

    def is_empty(self):
        return len(self.config_list) == 0

    def is_only_one_config(self):
        return len(self.config_list) == 1

    def is_more_than_one_config(self):
        return len(self.config_list) > 1


from ..exporter.default_exporter import default_exporter


class PopupExportMenu():
    def __init__(self, temp_path, context):
        self.path = temp_path
        self.context = context

    def default_image_menu(self, return_menu=False):
        context = self.context
        if context.area.type == "IMAGE_EDITOR":
            if context.area.spaces.active.image is not None and context.area.spaces.active.image.has_data is True:
                def draw_image_editor_menu(cls, context):
                    layout = cls.layout
                    layout.operator_context = "INVOKE_DEFAULT"
                    col = layout.column()
                    op = col.operator('spio.export_image')
                    op = col.operator('spio.export_pixel')

                if return_menu:
                    return draw_image_editor_menu

                context.window_manager.popup_menu(draw_image_editor_menu,
                                                  title=f'Super Export Image ({context.area.spaces.active.image.name})',
                                                  icon='IMAGE_DATA')

    def default_blend_menu(self, return_menu=False):
        context = self.context
        if context.area.type == "VIEW_3D":
            def draw_menu(cls, context):
                layout = cls.layout
                layout.operator_context = "INVOKE_DEFAULT"
                col = layout.column()
                col.operator('spio.export_blend', text='Export BLEND')

                for ext, bl_idname in default_exporter.items():
                    op = col.operator('spio.export_model', text=f'Export {ext.upper()}')
                    op.extension = ext

            if return_menu:
                return draw_menu

            context.window_manager.popup_menu(draw_menu,
                                              title=f'Super Export ({len(context.selected_objects)} objs)',
                                              icon='FILE_BLEND')


class PopupImportMenu():
    def __init__(self, file_list, context):
        self.file_list = file_list
        self.context = context

    def default_image_menu(self, return_menu=False):
        context = self.context
        join_paths = '$$'.join(self.file_list)

        if context.area.type == "VIEW_3D":
            def draw_3dview_menu(cls, context):
                layout = cls.layout
                layout.operator_context = "INVOKE_DEFAULT"
                # only one blend need to deal with
                col = layout.column()
                op = col.operator('spio.import_image', text=f'Import as reference')
                op.action = 'REF'
                op.files = join_paths

                op = col.operator('spio.import_image', text=f'Import as Plane')
                op.action = 'PLANE'
                op.files = join_paths

            if return_menu:
                return draw_3dview_menu

            context.window_manager.popup_menu(draw_3dview_menu,
                                              title=f'Super Import Image ({len(self.file_list)} files)',
                                              icon='IMAGE_DATA')
        elif context.area.type == "NODE_EDITOR":
            bpy.ops.spio.import_image(action='NODES', files=join_paths)

    def default_blend_menu(self, return_menu=False):
        context = self.context

        path = self.file_list[0]
        join_paths = '$$'.join(self.file_list)

        def draw_blend_menu(cls, context):
            pref = get_pref()
            layout = cls.layout
            layout.operator_context = "INVOKE_DEFAULT"
            # only one blend need to deal with
            if len(self.file_list) == 1:
                open = layout.operator('spio.open_blend', icon='FILEBROWSER')
                open.filepath = path

                open = layout.operator('spio.open_blend_extra', icon='ADD')
                open.filepath = path

                col = layout.column()

                col.separator()
                col.label(text='Append...', icon='APPEND_BLEND')
                for subpath, lib in default_blend_lib.items():
                    op = col.operator('spio.append_blend', text=subpath)
                    op.filepath = path
                    op.sub_path = subpath
                    op.data_type = lib

                col.separator()
                col.label(text='Link...', icon='LINK_BLEND')
                for subpath, lib in default_blend_lib.items():
                    op = col.operator('spio.link_blend', text=subpath)
                    op.filepath = path
                    op.sub_path = subpath
                    op.data_type = lib

            else:
                col = layout.column()
                op = col.operator('spio.batch_import_blend', text=f'Batch Open')
                op.action = 'OPEN'
                op.files = join_paths

                for subpath, lib in default_blend_lib.items():
                    op = col.operator('spio.batch_import_blend', text=f'Batch Append {subpath}')
                    op.action = 'APPEND'
                    op.files = join_paths
                    op.sub_path = subpath
                    op.data_type = lib

                col.separator()
                for subpath, lib in default_blend_lib.items():
                    op = col.operator('spio.batch_import_blend', text=f'Batch Link {subpath}')
                    op.action = 'LINK'
                    op.files = join_paths
                    op.sub_path = subpath
                    op.data_type = lib

        # return for combine drawing
        if return_menu:
            return draw_blend_menu
        # popup
        context.window_manager.popup_menu(draw_blend_menu,
                                          title=f'Super Import Blend ({len(self.file_list)} files)',
                                          icon='FILE_BLEND')

# def ray_cast(self, context, event):
#     # Get the mouse position
#     self.mouse_pos = event.mouse_region_x, event.mouse_region_y
#     # Contextual active object, 2D and 3D regions
#     scene = context.scene
#     region = context.region
#     region3D = context.space_data.region_3d
#
#     viewlayer = viewlayer_fix_291(self, context)
#
#     # The direction indicated by the mouse position from the current view
#     self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
#     # The view point of the user
#     self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
#     # The 3D location in this direction
#     self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)
#
#     result, self.loc, normal, index, self.object, matrix = scene.ray_cast(viewlayer, self.view_point,
#                                                                               self.view_vector)
#     print(result,self.object)
#     if result:
#         for obj in context.selected_objects:
#             obj.select_set(False)
#         # dg = context.evaluated_depsgraph_get()
#         # eval_obj = dg.id_eval_get(object)
#         # set active
#         context.view_layer.objects.active = self.object
