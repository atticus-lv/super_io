import bpy
import os
import shutil

from bpy.props import EnumProperty
from ..ui.icon_utils import RSN_Preview


class SPIO_OT_copy_c4d_plugin(bpy.types.Operator):
    bl_idname = 'spio.copy_c4d_plugin'
    bl_label = 'Install Cinema 4d Plugin'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout.box()
        layout.use_property_split = True

        layout.label(text='This is a plugin suitable for c4d R23+')
        layout.label(text="Copy the plugin folder under c4d's /plugins/")
        layout.label(text='You can find it in extension menu')

        file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", 'third_party_addons', 'Super IO for Cinema 4d v0.2'))
        full_path = os.path.abspath(file)

        layout.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = full_path


def set_hou_package_config(package_path, version='19.0'):
    d = f"""
    {{
	"env": [
		{{
			"SPIO": "{package_path}"
		}},
		{{
			"HOUDINI_PYTHONWARNINGS": "ignore"
		}}
	],
	"path": "$SPIO"
	
    }}
    """

    doc_path = os.path.expanduser('~\Documents')
    package_config_path = os.path.join(doc_path, f'houdini{version}', 'packages')
    if not os.path.exists(package_config_path):
        os.makedirs(package_config_path)
    fp = os.path.join(package_config_path, 'SPIO.json')

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(d)


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Install Houdini Package'

    version: EnumProperty(name='Version', items=[
        ('19.0', '19.0', ''),
        ('18.5', '18.5', ''),
        ('18.0', '18.0', ''),
    ])

    def execute(self, context):
        package_path = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'Super IO for Houdini v0.3').replace('\\', '/')

        set_hou_package_config(package_path, self.version)
        self.report({"INFO"}, 'Successfully Write Package json File')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout.box()
        layout.use_property_split = True

        layout.label(text='This is a script suitable for houdini 18+(python3)')
        layout.label(text="Click 'Install' to auto install, 'Tutorial' to check tutorial image")
        layout.label(text='Then assign Shortcut for it')
        layout.separator()

        layout.prop(self, 'version')

        layout.operator_context = "EXEC_DEFAULT"
        layout.operator('spio.copy_houdini_script', text='Install', icon='IMPORT').version = self.version

        layout.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'Super IO for Houdini v0.3')


class SPIO_OT_load_text(bpy.types.Operator):
    bl_idname = 'spio.load_text'
    bl_label = 'Load Text'

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        with open(self.filepath, 'r') as f:
            filename = os.path.basename(self.filepath)
            text = f.read()
            if filename in bpy.data.texts: bpy.data.texts.remove(bpy.data.texts[filename])

            t = bpy.data.texts.new(name=filename)
            t.write(text)

        bpy.ops.spio.pop_editor(editor_text=filename)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_load_text)
    bpy.utils.register_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.register_class(SPIO_OT_copy_houdini_script)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_load_text)
    bpy.utils.unregister_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.unregister_class(SPIO_OT_copy_houdini_script)
