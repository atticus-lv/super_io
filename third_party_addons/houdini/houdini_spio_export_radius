# v0.1
# Initial Win

import os
import hou
import subprocess

TEMP_DIR = ''

icon_config = {
    "abc": 'SOP_alembic',
    "vdb": 'SOP_OpenVDB',
    "obj": 'SOP_file',
    "stl": 'SOP_file',
}

# TODO rop node for animation later
# rop_export = ['fbx', 'abc']


def get_dir():
    global TEMP_DIR
    if TEMP_DIR == '':
        TEMP_DIR = os.path.join(os.path.expanduser('~'), 'spio_temp')
        if not "spio_temp" in os.listdir(os.path.expanduser('~')):
            os.makedirs(TEMP_DIR)

    return TEMP_DIR


def save_file(ext):
    file_list = list()

    for node in hou.selectedNodes():
        name = node.path().split('/')[-1]
        filepath = os.path.join(get_dir(), name + '.' + ext)
        node.geometry().saveToFile(filepath)
        file_list.append(filepath)
    # push to clipboard
    clipboard = PowerShellClipboard()
    clipboard.push_to_clipboard(paths=file_list)


def generate_menu():
    menu_type = 'script_action'
    menu = dict()

    for i, (ext, icon) in enumerate(icon_config.items()):
        d = {
            'type': menu_type,
            'label': f'Export {ext.upper()}',
            'icon': icon,
            'script': lambda ext=ext, **kwargs: save_file(ext),
        }
        menu[f'{i * 2}'] = d  # assign location

    return menu

class PowerShellClipboard():
    def __init__(self, file_urls=None):
        pass

    def get_args(self, script):
        powershell_args = [
            os.path.join(
                os.getenv("SystemRoot"),
                "System32",
                "WindowsPowerShell",
                "v1.0",
                "powershell.exe",
            ),
            "-NoProfile",
            "-NoLogo",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
        ]
        script = (
                "$OutputEncoding = "
                "[System.Console]::OutputEncoding = "
                "[System.Console]::InputEncoding = "
                "[System.Text.Encoding]::UTF8; "
                + "$PSDefaultParameterValues['*:Encoding'] = 'utf8'; "
                + script
        )
        args = powershell_args + ["& { " + script + " }"]
        return args

    def push(self, script):
        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        subprocess.Popen(**parms)

    def push_to_clipboard(self, paths):
        join_s = ""

        for path in paths:
            join_s += f", '{path}'"

        script = (
            f"$filelist = {join_s};"
            "$col = New-Object Collections.Specialized.StringCollection; "
            "foreach($file in $filelist){$col.add($file)}; "
            "Add-Type -Assembly System.Windows.Forms; "
            "[System.Windows.Forms.Clipboard]::SetFileDropList($col); "
        )

        self.push(script)


radialmenu.setRadialMenu(generate_menu())
