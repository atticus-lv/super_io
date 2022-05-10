import os
import hou

TEMP_DIR = ''


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

    clipboard = PowerShellClipboard()
    clipboard.push_to_clipboard(paths=file_list)


import subprocess


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


menu = {
    "n": {
        "type": "script_action",
        "label": "Export ABC",
        "script": lambda ext='vdb', **kwargs: save_file(ext),
    },
    "s": {
        "type": "script_action",
        "label": "Export OBJ",
        "script": lambda ext='obj', **kwargs: save_file(ext),
    },
    "e": {
        "type": "script_action",
        "label": "Export STL",
        "script": lambda ext='stl', **kwargs: save_file(ext)
    },
    "w": {
        "type": "script_action",
        "label": "Export VDB",
        "script": lambda ext='vdb', **kwargs: save_file(ext),
    }
}

radialmenu.setRadialMenu(menu)
