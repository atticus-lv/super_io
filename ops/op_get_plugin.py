import bpy
import os
import shutil
from pathlib import Path
from os.path import expanduser

from bpy.props import EnumProperty


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


def set_hou_package_config(pointer_path, package_config_path):
    d = f"""
    {{
	"env": [
		{{
			"SPIO": "{pointer_path}"
		}},
		{{
			"HOUDINI_PYTHONWARNINGS": "ignore"
		}}
	],
	"path": "$SPIO"
	
    }}
    """
    print(package_config_path)
    if not os.path.exists(package_config_path):
        os.mkdir(package_config_path)
    fp = package_config_path + '/' + 'SPIO.json'

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(d)


def init_package_path(self, context):
    setattr(self, 'package_path',
            os.path.join(expanduser('~\Documents'), f'houdini{self.version}', 'packages'))


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Install Houdini Package'
    bl_options = {'REGISTER', 'UNDO'}

    version: EnumProperty(name='Version', items=[
        ('19.5', '19.5', ''),
        ('19.0', '19.0', ''),
        ('18.5', '18.5', ''),
        ('18.0', '18.0', ''),
    ], update=init_package_path, default='19.0')

    package_path: bpy.props.StringProperty(name='Packages Path', default='', subtype='DIR_PATH')

    def execute(self, context):
        pointer_path = Path(__file__).parent.parent.joinpath('third_party_addons', 'Super IO for Houdini v0.3').resolve()

        package_path = Path(self.package_path).resolve()

        set_hou_package_config(str(pointer_path).replace('\\', '/'), str(package_path).replace('\\', '/'))

        self.report({"INFO"}, 'Successfully Write Package json File')
        return {'FINISHED'}

    def invoke(self, context, event):
        init_package_path(self, context)
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout.box()
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.use_property_split = True

        layout.label(text='This is a script suitable for houdini 18+(python3)')
        layout.label(text="Click 'Install' to auto install, 'Tutorial' to check tutorial image")
        layout.label(text='Then assign Shortcut for it')
        layout.separator()

        layout.prop(self, 'version')
        layout.prop(self, 'package_path')

        layout.operator_context = "EXEC_DEFAULT"
        layout.operator('spio.copy_houdini_script', text='Install', icon='IMPORT').package_path = self.package_path

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
