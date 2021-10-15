import os
import time
import subprocess

import bpy
from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from ..clipboard.wintypes import WintypesClipboard as Clipboard
from .utils import get_config, is_float, get_pref, MeasureTime

from ..ui.icon_utils import RSN_Preview

import_icon = RSN_Preview(image='import.bip', name='import_icon')


class TEMP_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        row.prop(item, 'name', text='', emboss=False)
        row.prop(item, 'bl_idname', text='', emboss=False)

    def draw_filter(self, context, layout):
        # hide to prevent edit by user
        pass

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        ordered = []
        filtered = [self.bitflag_filter_item] * len(items)

        # get current filter extension
        ext = context.scene.spio_ext

        for i, item in enumerate(items):
            if item['extension'] == ext:
                filtered[i] &= ~self.bitflag_filter_item

        if filtered:
            show_flag = self.bitflag_filter_item & ~self.bitflag_filter_item
            for i, bitflag in enumerate(filtered):
                if bitflag == show_flag:
                    filtered[i] = self.bitflag_filter_item
                else:
                    filtered[i] &= ~self.bitflag_filter_item
        try:
            ordered = bpy.types.UI_UL_list.sort_items_helper(items, lambda i: len(i['extension' == ext]),
                                                             True)
        except:
            pass

        return filtered, ordered


class blenderFileDefault:
    bl_label = 'blenderFileDefault'
    bl_options = {'UNDO_GROUPED'}

    filepath: StringProperty()
    sub_path: StringProperty()

    # batch mode
    load_all = False
    data_type: StringProperty()

    # link
    link = False

    def load_batch(self):
        with bpy.data.libraries.load(self.filepath, link=self.link) as (data_from, data_to):
            if self.data_type in {'materials', 'worlds'}:
                setattr(data_to, self.data_type, getattr(data_from, self.data_type))

            elif self.data_type == 'collections':
                data_to.collections = [name for name in data_from.collections]

            elif self.data_type == 'objects':
                data_to.objects = [name for name in data_from.objects]

        for coll in data_to.collections:
            bpy.context.scene.collection.children.link(coll)

        for obj in data_to.objects:
            bpy.context.collection.objects.link(obj)

    def load_with_ui(self):
        if self.link:
            bpy.ops.wm.link('INVOKE_DEFAULT',
                            filepath=self.filepath if self.sub_path == '' else os.path.join(self.filepath,
                                                                                            self.sub_path))
        else:
            bpy.ops.wm.append('INVOKE_DEFAULT',
                              filepath=self.filepath if self.sub_path == '' else os.path.join(self.filepath,
                                                                                              self.sub_path))

    def invoke(self, context, event):
        self.load_all = event.alt
        # self.link = event.shift
        return self.execute(context)

    def execute(self, context):
        # seem need to return set for invoke
        if not self.load_all:
            self.load_with_ui()
            return {'FINISHED'}
        else:
            self.load_batch()
            self.report({"INFO"}, f'Load all {self.data_type} from {self.filepath}')
            return {'FINISHED'}


class SPIO_OT_AppendBlend(blenderFileDefault, bpy.types.Operator):
    """Alt to load all from this data type"""
    bl_idname = 'wm.spio_append_blend'
    bl_label = 'Append...'

    link = False


class SPIO_OT_LinkBlend(blenderFileDefault, bpy.types.Operator):
    """Alt to load all from this data type"""
    bl_idname = 'wm.spio_link_blend'
    bl_label = 'Link...'

    link = True


class SPIO_OT_OpenBlend(blenderFileDefault, bpy.types.Operator):
    """Open/Load file with an other blender"""
    bl_idname = 'wm.spio_open_blend'
    bl_label = 'Open...'

    load: BoolProperty()

    def execute(self, context):
        if self.load:
            bpy.ops.wm.open_mainfile(filepath=self.filepath)
        else:
            subprocess.Popen([bpy.app.binary_path, self.filepath])
        return {"FINISHED"}


class SuperImport(bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # dependant
    dep_classes = []
    # data
    clipboard = None
    file_list = []
    ext = ''
    # state
    use_custom_config = False
    config_list_index: IntProperty(name='Active Index')
    # UI
    show_urls: BoolProperty(default=False, name='Show Files')
    show_property: BoolProperty(default=False, name='Edit Property')

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        row = layout.row()
        row.alignment = "LEFT"
        row.prop(self, 'show_urls', text=f'Import {len(self.file_list)} {self.ext} Object',
                 icon_value=import_icon.get_image_icon_id(), emboss=False)
        row.separator()
        row.prop(self, 'update')

        if self.show_urls:
            col = layout.column(align=True)
            for file_path in self.file_list:
                col.label(text=str(file_path))

        layout.template_list(
            "TEMP_UL_ConfigList", "Config List",
            pref, "config_list",
            self, "config_list_index", rows=4)

        item = pref.config_list[self.config_list_index]

        box = layout.box().split().column()

        row = box.split(factor=0.25)
        row.prop(self, 'show_property', icon='TRIA_DOWN' if self.show_property else "TRIA_RIGHT", emboss=False,
                 text=item.name)
        row = row.row(align=True)

        row.label(text=item.description)
        c = row.operator('spio.config_list_copy', text='', icon='DUPLICATE')
        c.index = self.config_list_index

        if not self.show_property: return

        if item.bl_idname != '':
            row = box.row()
            if len(item.prop_list) != 0:
                row.label(text='Property')
                row.label(text='Value')
            for prop_index, prop_item in enumerate(item.prop_list):
                row = box.row()
                row.prop(prop_item, 'name', text='')
                row.prop(prop_item, 'value', text='')

                d = row.operator('wm.spio_operator_prop_remove', text='', icon='PANEL_CLOSE', emboss=False)
                d.config_list_index = self.config_list_index
                d.prop_index = prop_index

        row = box.row(align=True)
        row.alignment = 'LEFT'
        d = row.operator('wm.spio_operator_prop_add', text='Add Property', icon='ADD', emboss=False)
        d.config_list_index = self.config_list_index

    def invoke(self, context, event):
        # restore
        self.file_list.clear()
        self.clipboard = None
        self.ext = None

        self.clipboard = Clipboard()
        self.file_list = self.clipboard.push(force_unicode=get_pref().force_unicode)

        del self.clipboard  # release clipboard

        if len(self.file_list) == 0:
            self.report({"ERROR"}, "No file found in clipboard")
            return {"CANCELLED"}

        for file_path in self.file_list:
            extension = file_path.split('.')[-1].lower()
            if self.ext is None:
                self.ext = extension
            elif self.ext != extension:
                self.report({"ERROR"}, "Only one type of file can be imported at a time")
                return {"CANCELLED"}

        # get extension
        context.scene.spio_ext = self.ext

        config, index_list = get_config(get_pref().config_list, check_use=True, filter=context.scene.spio_ext,
                                        return_index=True)
        # import default if not custom config for this file extension
        if len(config) == 0:
            self.use_custom_config = False

            if self.ext == 'blend':
                self.import_blend_default(context)
                return {'FINISHED'}
            else:
                return self.execute(context)

        elif len(config) >= 1:
            self.use_custom_config = True

            if len(config) == 1:
                self.config_list_index = index_list[0]
                return self.execute(context)

            elif len(config) > 1:
                self.config_list_index = index_list[0]
                if get_pref().import_style == 'PANEL':
                    return context.window_manager.invoke_props_dialog(self, width=450)
            return self.import_custom_dynamic(context, index_list)

    def execute(self, context):
        with MeasureTime() as start_time:
            if self.use_custom_config is False:
                self.import_default()
            else:
                self.import_custom()

            if get_pref().report_time: self.report({"INFO"},
                                                   f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        # unregister dynamic class
        # for cls in self.dep_classes:
        #     bpy.utils.unregister_class(cls)

        return {"FINISHED"}

    def import_custom_dynamic(self, context, index_list):
        # clear
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)
        self.dep_classes.clear()

        file_list = self.file_list

        for index in index_list:
            config_item = get_pref().config_list[index]

            def execute(self, context):
                config_item = get_pref().config_list[index]
                ops_args = dict()

                for prop_item in config_item.prop_list:

                    prop = prop_item.name
                    value = prop_item.value

                    print(prop, value)

                    if prop == '' or value == '': continue

                    if value.isdigit():
                        ops_args[prop] = int(value)
                    elif is_float(value):
                        ops_args[prop] = float(value)
                    elif value in {'True', 'False'}:
                        ops_args[prop] = eval(value)
                    else:
                        ops_args[prop] = value

                bl_idname = config_item.bl_idname
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

                if op_callable:
                    for file_path in file_list:
                        ops_args['filepath'] = file_path
                        try:
                            op_callable(**ops_args)
                        except Exception as e:
                            self.report({"ERROR"}, str(e))
                else:
                    self.report({"ERROR"}, f'{op_callable} Error!!!')

                return {"FINISHED"}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": config_item.name,
                           "bl_description": config_item.description,
                           "execute": execute, },
                          )

            self.dep_classes.append(op_cls)





        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        import_op = self

        def draw_custom_menu(self, context):
            for cls in import_op.dep_classes:
                self.layout.operator(cls.bl_idname)

        context.window_manager.popup_menu(draw_custom_menu,
                                          title='Super Import Custom',
                                          icon='FILE')

        return {'FINISHED'}

    def import_custom(self):
        """import users' custom configs"""
        config_item = get_pref().config_list[self.config_list_index]
        ops_args = dict()

        for prop_index, prop_item in enumerate(config_item.prop_list):
            prop = prop_item.name
            value = prop_item.value

            if prop == '' or value == '': continue

            if value.isdigit():
                ops_args[prop] = int(value)
            elif is_float(value):
                ops_args[prop] = float(value)
            elif value in {'True', 'False'}:
                ops_args[prop] = eval(value)
            else:
                ops_args[prop] = value

        bl_idname = config_item.bl_idname
        op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

        if op_callable:
            for file_path in self.file_list:
                ops_args['filepath'] = file_path
                try:
                    op_callable(**ops_args)
                except Exception as e:
                    self.report({"ERROR"}, str(e))

    def import_default(self):
        """Import with blender's default setting"""
        pass

    def import_blend_default(self, context):
        # self.register_default_blend_import()

        path = self.file_list[0]

        data_type = [
            'collection',
            'material',
            'world',
            'object'
        ]

        data_type_title = [d.title() for d in data_type]
        data_type_s = [d + 's' for d in data_type]

        def draw_blend_menu(cls, context):
            pref = get_pref()
            layout = cls.layout
            layout.operator_context = "INVOKE_DEFAULT"

            if pref.simple_blend_menu:
                layout.operator('wm.spio_append_blend', icon='APPEND_BLEND')
                layout.operator('wm.spio_link_blend', icon='LINK_BLEND')

                open = layout.operator('wm.spio_open_blend', icon='ADD')
                open.filepath = path
                open.load = False
                open = layout.operator('wm.spio_open_blend', icon='FILE_TICK', text='Load')
                open.filepath = path
                open.load = True
            else:

                col = layout.column()

                open = col.operator('wm.spio_open_blend', icon='ADD')
                open.filepath = path
                open.load = False

                open = col.operator('wm.spio_open_blend', icon='FILE_TICK', text='Load')
                open.filepath = path
                open.load = True

                col.separator()
                col.label(text='Append...', icon='APPEND_BLEND')
                for idx, d in enumerate(data_type):
                    ops = col.operator('wm.spio_append_blend', text=data_type_title[idx])
                    ops.filepath = path
                    ops.sub_path = data_type_title[idx]
                    ops.data_type = data_type_s[idx]

                col.separator()
                col.label(text='Link...', icon='LINK_BLEND')
                for idx, d in enumerate(data_type):
                    ops = col.operator('wm.spio_link_blend', text=data_type_title[idx])
                    ops.filepath = path
                    ops.sub_path = data_type_title[idx]
                    ops.data_type = data_type_s[idx]

        context.window_manager.popup_menu(draw_blend_menu,
                                          title='Super Import Blend',
                                          icon='FILE_BLEND')


class VIEW3D_OT_SuperImport(SuperImport):
    bl_idname = "view3d.spio_import"
    bl_label = "Super Import View3D"

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return context.area.ui_type == "VIEW_3D" and context.mode == "OBJECT"
        #
        # elif context.area.type == "NODE_EDITOR":
        #     return context.area.ui_type == "ShaderNodeTree" and context.space_data.edit_tree is not None

    def import_default(self):
        ext = self.ext
        for file_path in self.file_list:
            path = file_path
            if ext in {'usd', 'usdc', 'usda'}:
                bpy.ops.wm.usd_import(filepath=file_path)
            elif ext == 'ply':
                bpy.ops.import_mesh.ply(filepath=path)
            elif ext == 'stl':
                bpy.ops.import_mesh.stl(filepath=path)
            elif ext == 'dae':
                bpy.ops.wm.collada_import(filepath=path)
            elif ext == 'abc':
                bpy.ops.wm.alembic_import(filepath=path)
            elif ext == 'obj':
                bpy.ops.import_scene.obj(filepath=path)
            elif ext == 'fbx':
                bpy.ops.import_scene.fbx(filepath=path)
            elif ext in {'glb', 'gltf'}:
                bpy.ops.import_scene.gltf(filepath=path)
            elif ext in {'x3d', 'wrl'}:
                bpy.ops.import_scene.x3d(filepath=path)
            elif ext == 'svg':
                bpy.ops.import_curve.svg(filepath=path)
            else:
                bpy.ops.object.load_reference_image(filepath=path)


class NODE_OT_SuperImport(SuperImport):
    bl_idname = "node.spio_import"
    bl_label = "Super Import ShaderNodeTree"

    @classmethod
    def poll(_cls, context):
        return (
                context.area.type == "NODE_EDITOR"
                and context.area.ui_type == "ShaderNodeTree"
                and context.space_data.edit_tree is not None
        )

    def import_default(self):
        nt = bpy.context.space_data.edit_tree
        location_X, location_Y = bpy.context.space_data.cursor_location
        for file_path in self.file_list:
            tex_node = nt.nodes.new("ShaderNodeTexImage")
            tex_node.location = location_X, location_Y
            # tex_node.hide = True
            location_Y += 250

            path = file_path
            image = bpy.data.images.load(filepath=path)
            tex_node.image = image


def file_context_menu(self, context):
    layout = self.layout
    layout.operator('view3d.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def node_context_menu(self, context):
    layout = self.layout
    layout.operator('node.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def register():
    import_icon.register()

    bpy.utils.register_class(TEMP_UL_ConfigList)
    bpy.utils.register_class(SPIO_OT_AppendBlend)
    bpy.utils.register_class(SPIO_OT_LinkBlend)
    bpy.utils.register_class(SPIO_OT_OpenBlend)
    bpy.utils.register_class(VIEW3D_OT_SuperImport)
    bpy.utils.register_class(NODE_OT_SuperImport)

    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')
    bpy.types.TOPBAR_MT_file_context_menu.prepend(file_context_menu)
    bpy.types.NODE_MT_context_menu.prepend(node_context_menu)


def unregister():
    import_icon.unregister()

    bpy.types.TOPBAR_MT_file_context_menu.remove(file_context_menu)
    bpy.types.NODE_MT_context_menu.remove(node_context_menu)

    bpy.utils.unregister_class(TEMP_UL_ConfigList)
    bpy.utils.unregister_class(VIEW3D_OT_SuperImport)
    bpy.utils.unregister_class(SPIO_OT_AppendBlend)
    bpy.utils.unregister_class(SPIO_OT_LinkBlend)
    bpy.utils.unregister_class(SPIO_OT_OpenBlend)
    bpy.utils.unregister_class(NODE_OT_SuperImport)
