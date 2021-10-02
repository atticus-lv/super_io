import bpy
from bpy.props import EnumProperty, CollectionProperty, StringProperty, IntProperty, BoolProperty
from ..clipboard.windows import WindowsClipboard as Clipboard
from .utils import get_config, is_float, get_pref


class Temp_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.label(text=item.bl_idname)

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


class VIEW3D_OT_SuperImport(bpy.types.Operator):
    """Paste Model/Images"""

    bl_idname = "view3d.spio_import"
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

    @classmethod
    def poll(_cls, context):
        return (
                context.area.type == "VIEW_3D"
                and context.area.ui_type == "VIEW_3D"
                and context.mode == "OBJECT"
        )

    def draw(self, context):
        layout = self.layout
        pref = get_pref()

        layout.prop(self, 'show_urls', icon='INFO', text=f'Import {len(self.file_list)} {self.ext} Object')
        if self.show_urls:
            col = layout.column(align=1)
            for file in self.file_list:
                col.label(text=str(file.filepath))

        layout.template_list(
            "Temp_UL_ConfigList", "Task List",
            pref, "config_list",
            self, "config_list_index")

        item = pref.config_list[self.config_list_index]
        layout.prop(item, 'bl_idname')

        box = layout.column().box()

        row = box.row()
        row.label(text='Property Name')
        row.label(text='Property Value')

        for prop_item in item.prop_list:
            row = box.row()
            row.prop(prop_item, 'name', text='')
            row.prop(prop_item, 'value', text='')

    def invoke(self, context, event):
        self.clipboard = Clipboard.push()
        tmp_ext = []
        if self.clipboard is None:
            return {"CANCELLED"}

        for file in self.clipboard.file_urls:
            self.file_list.append(file)
            extension = file.filepath.split('.')[-1].lower()
            if extension not in tmp_ext:
                tmp_ext.append(extension)
            if len(tmp_ext) > 1:
                self.report({"ERROR"}, "Only one type of file can be imported at a time")
                return {"CANCELLED"}

        # get extension
        self.ext = tmp_ext[0]
        config = get_config(get_pref().config_list, check_use=True, filter=self.ext)

        # import default if not custom config for this file extension
        if len(config) == 0:
            self.use_custom_config = False
            return self.execute(context)

        self.use_custom_config = True
        context.scene.spio_ext = self.ext

        return context.window_manager.invoke_props_dialog(self, width=450)

    def execute(self, context):
        if self.use_custom_config is False:
            self.import_default()
        else:
            self.import_custom()
        return {"FINISHED"}

    def import_custom(self):
        for file in self.clipboard.file_urls:
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

            ops_args['filepath'] = file.filepath
            bl_idname = config_item.bl_idname

            try:
                print(f'bpy.ops.{bl_idname}(**{ops_args})')
                exec(f'bpy.ops.{bl_idname}(**{ops_args})')
            except Exception as e:
                self.report({"ERROR"}, str(e))

    def import_default(self):
        """Import with blender's default setting"""
        ext = self.ext
        for file in self.file_list:
            if ext in {'usd', 'usdc', 'usda'}:
                bpy.ops.wm.usd_import(filepath=file.filepath)
            elif ext == 'ply':
                bpy.ops.import_mesh.ply(file.filepath)
            elif ext == 'stl':
                bpy.ops.import_mesh.stl(filepath=file.filepath)
            elif ext == 'dae':
                bpy.ops.wm.collada_import(filepath=file.filepath)
            elif ext == 'abc':
                bpy.ops.wm.alembic_import(filepath=file.filepath)
            elif ext == 'obj':
                bpy.ops.import_scene.obj(filepath=file.filepath)
            elif ext == 'fbx':
                bpy.ops.import_scene.fbx(filepath=file.filepath)
            elif ext in {'glb', 'gltf'}:
                bpy.ops.import_scene.gltf(filepath=file.filepath)
            elif ext in {'x3d', 'wrl'}:
                bpy.ops.import_scene.x3d(filepath=file.filepath)
            elif ext == 'svg':
                bpy.ops.import_curve.svg(filepath=file.filepath)
            else:
                bpy.ops.object.load_reference_image(filepath=file.filepath)


def register():
    bpy.utils.register_class(Temp_UL_ConfigList)
    bpy.utils.register_class(VIEW3D_OT_SuperImport)

    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')


def unregister():
    bpy.utils.unregister_class(Temp_UL_ConfigList)
    bpy.utils.unregister_class(VIEW3D_OT_SuperImport)
