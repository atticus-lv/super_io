import bpy
import os
from os.path import join
from ..preferences.prefs import get_pref

import re

rule = r'op.(.*?) = (.*)'


def get_presets(bl_idname):
    preset_paths = []
    dir = join(bpy.utils.user_resource('SCRIPTS'), 'presets', 'operator')
    for f in os.listdir(dir):
        fp = join(dir, f)

        if f != bl_idname: continue
        if not os.path.isdir(fp): continue

        for file in os.listdir(fp):
            if not file.endswith('.py'): continue

            path = join(fp, file)
            preset_paths.append(path)
        break

    return preset_paths


def get_preset_chars(path):
    args = {}
    with open(path, 'r') as f:
        lines = f.read()
        res = re.findall(rule, lines)

        if not res: return args
        for t in res:
            key = t[0]
            value = t[1]

            if value.startswith('{'):
                continue  # pass set type
            elif key == 'filepath':
                continue  # pass filepath
            elif value.startswith("'") and t[1].endswith("'"):
                value = t[1][1:-1]

            args[key] = value

    return args


class SPIO_OT_read_preset(bpy.types.Operator):
    bl_idname = "spio.read_preset"
    bl_label = "Add from Preset"
    bl_options = {'INTERNAL'}

    bl_idname_input: bpy.props.StringProperty(name="ID Name")

    dep_classes = []

    def invoke(self, context, event):
        # clear
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)

        self.dep_classes.clear()

        preset_paths = get_presets(self.bl_idname_input)
        if len(preset_paths) == 0:
            self.report({'ERROR'}, "No preset found")
            return {'CANCELLED'}

        for i, path in enumerate(preset_paths):
            name = os.path.basename(path)

            def execute(self, context):
                config_item = get_pref().config_list[get_pref().config_list_index]
                args = get_preset_chars(self.path)
                prop_list = config_item.prop_list

                for key, value in args.items():
                    if key in prop_list:
                        prop_list[key].value = value
                    else:
                        prop_item = prop_list.add()
                        prop_item.name = key
                        prop_item.value = value

                return {'FINISHED'}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_set_preset_{i}',
                           "bl_label": name[:-3],  # remove .py
                           "execute": execute,
                           # custom pass in
                           'path': path,
                           },
                          )

            self.dep_classes.append(op_cls)

        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        op = self

        def draw_preset_menu(self, context):
            layout = self.layout
            layout.label(text="Preset")
            for cls in op.dep_classes:
                layout.operator(cls.bl_idname)

        context.window_manager.popup_menu(draw_preset_menu)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_read_preset)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_read_preset)
