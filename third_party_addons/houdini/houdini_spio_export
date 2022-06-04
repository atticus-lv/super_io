# log
# v0.1
# initial win
# v0.2
# add export format menu
# v0.3
# add alembic animation export

from __future__ import annotations

import sys

import hou
import os
import numpy as np

# Custom Temp Path
TEMP_DIR = ''

# label in the popup list
export_labels = [
    'Wavefront (.obj)',
    'Alembic (.abc)',
    'OpenVDB (.vdb)',
    'Stl (.stl)',
    'AutoCAD DXF(.dxf)',
    'Stanford (.ply)',
    # animation format
    'Alembic Animation (.abc)'
]

# format to export
export_formats = [
    'obj', 'abc', 'vdb', 'stl', 'dxf', 'ply',
    'anim-abc'
]


def get_dir():
    """get temp dir

    """
    global TEMP_DIR
    if TEMP_DIR == '':
        TEMP_DIR = os.path.join(os.path.expanduser('~'), 'spio_temp')
        if not "spio_temp" in os.listdir(os.path.expanduser('~')):
            os.makedirs(TEMP_DIR)
    return TEMP_DIR


def get_export_config():
    """create pop up list

    """
    index = hou.ui.selectFromList(export_labels,
                                  default_choices=(), exclusive=True, message="Select a format to export",
                                  title='Super Export',
                                  column_header=None,
                                  num_visible_rows=10, clear_on_cancel=False, width=250, height=300)
    return index[0] if len(index) != 0 else None


def main():
    """run the whole script

    """
    if sys.platform != "win32":
        return print("Not Support this platform!")

    # create or set nodes
    if len(hou.selectedNodes()) == 0:
        return

    file_list = list()

    res = get_export_config()
    if res is None: return

    # get ext
    ext = export_formats[res]

    for node in hou.selectedNodes():
        # get name
        name = node.path().split('/')[-1]

        # current frame
        if not ext.startswith('anim'):
            filepath = os.path.join(get_dir(), name + '.' + ext)
            node.geometry().saveToFile(filepath)
            file_list.append(filepath)

        # animation file
        elif ext == 'anim-abc':
            filepath = os.path.join(get_dir(), name + '.' + 'abc')

            # create_node
            paneTabObj = hou.ui.paneTabUnderCursor()
            parent = paneTabObj.pwd()
            r_node = parent.createNode('rop_alembic')

            # set position, not need, will destroy node later
            # net_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            # cursor_pos = net_editor.cursorPosition()
            # pos = np.subtract(cursor_pos, [-0.5, -1])
            # r_node.setPosition(pos)

            # connect, set parm
            r_node.setInput(0, node)
            r_node.parm('filename').set(filepath)
            r_node.parm('trange').set(1)
            # render
            r_node.render(output_progress=True)  # log window

            # destroy
            r_node.destroy()
            file_list.append(filepath)

    # push to clipboard
    clipboard = PowerShellClipboard()
    clipboard.push_to_clipboard(paths=file_list)


#### Clipboard ####

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


# run
main()
