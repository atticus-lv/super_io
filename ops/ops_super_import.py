import bpy
import time

from bpy.props import EnumProperty, CollectionProperty, StringProperty, IntProperty, BoolProperty

from ..clipboard.wintypes import WintypesClipboard as Clipboard
from .utils import get_config, is_float, get_pref, MeasureTime

from ..ui.icon_utils import RSN_Preview

import_icon = RSN_Preview(image='import.bip', name='import_icon')


class TEMP_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        row.prop(item, 'name', text='', emboss=False)
        row.prop(item, 'bl_idname', text='', emboss=False)

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

# import bpy
#
# for i in range(10):
#     idname = "object.operator_%d" % i
#
#     def func(self, context):
#         print("Hello World", self.bl_idname)
#         return {'FINISHED'}
#
#     opclass = type("DynOp%d" % i,
#                    (bpy.types.Operator, ),
#                    {"bl_idname": idname, "bl_label": "Test", "execute": func},
#                    )
#     bpy.utils.register_class(opclass)

class SuperImport(bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # data
    clipboard = None
    file_list = []
    ext = ''
    # state
    use_custom_config = False
    config_list_index: IntProperty(name='Active Index')
    # UI
    show_urls: BoolProperty(default=False, name='Show Files')

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        row = layout.row()
        row.alignment = "LEFT"
        row.prop(self, 'show_urls', text=f'Import {len(self.file_list)} {self.ext} Object',
                 icon_value=import_icon.get_image_icon_id(), emboss=False)
        row.separator()

        if self.show_urls:
            col = layout.column(align=True)
            for file_path in self.file_list:
                col.label(text=str(file_path))

        layout.template_list(
            "TEMP_UL_ConfigList", "Config List",
            pref, "config_list",
            self, "config_list_index")

        item = pref.config_list[self.config_list_index]

        box = layout.box().split().column(align=True)

        box.label(text=item.name, icon='EDITMODE_HLT')
        row = box.row()
        row.label(text='Property Name')
        row.label(text='Property Value')

        for prop_item in item.prop_list:
            row = box.row()
            row.prop(prop_item, 'name', text='')
            row.prop(prop_item, 'value', text='')

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
            return self.execute(context)
        elif len(config) >= 1:
            self.use_custom_config = True

            if len(config) == 1:
                self.config_list_index = index_list[0]
                return self.execute(context)

            if len(config) > 1:
                self.config_list_index = index_list[0]
                return context.window_manager.invoke_props_dialog(self,width=450)

    def execute(self, context):
        with MeasureTime() as start_time:
            if self.use_custom_config is False:
                self.import_default()
            else:
                self.import_custom()

            if get_pref().report_time: self.report({"INFO"},
                                                   f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

            return {"FINISHED"}

    def import_custom(self):
        """import users' custom configs"""
        for file_path in self.file_list:
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

            ops_args['filepath'] = file_path
            bl_idname = config_item.bl_idname

            try:
                exec(f'bpy.ops.{bl_idname}(**{ops_args})')
            except Exception as e:
                self.report({"ERROR"}, str(e))

    def import_default(self):
        """Import with blender's default setting"""
        pass


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
    bpy.utils.unregister_class(NODE_OT_SuperImport)
