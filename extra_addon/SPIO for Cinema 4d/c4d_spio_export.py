# log
# v1.0
# initial win

import c4d
from c4d import gui, plugins

import os

# Custom Temp Path
TEMP_DIR = ''


def get_dir():
    global TEMP_DIR
    if TEMP_DIR == '':
        TEMP_DIR = os.path.join(os.path.expanduser('~'), 'spio_temp')
        if not "spio_temp" in os.listdir(os.path.expanduser('~')):
            os.makedirs(TEMP_DIR)

    return TEMP_DIR


def main():
    filename = c4d.documents.GetActiveDocument().GetDocumentName()
    filePath = os.path.join(get_dir(), filename + '.fbx')
    # c4d.storage.LoadDialog(title="Test", flags=c4d.FILESELECT_SAVE, force_suffix="abc")

    # Retrieves FBX exporter plugin, 1026370
    fbxExportId = 1026370
    plug = plugins.FindPlugin(fbxExportId, c4d.PLUGINTYPE_SCENESAVER)
    if plug is None:
        return gui.MessageDialog('Failed to retrieves Exporter!')
    # check exporter
    op = dict()

    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
        return gui.MessageDialog('Failed to retrieves private data')

    fbxExport = op.get("imexporter", None)
    if fbxExport is None:
        return gui.MessageDialog('Exporter Not Found!')

    # set fbx exporter
    fbxExport[c4d.FBXEXPORT_ASCII] = False
    fbxExport[c4d.FBXEXPORT_SELECTION_ONLY] = True

    # save
    if not c4d.documents.SaveDocument(doc, filePath, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, fbxExportId):
        return gui.MessageDialog('Exporter Failed!')

    print("Document successfully exported to:", filePath)
    # copy
    clipboard = PowerShellClipboard()
    clipboard.push_to_clipboard(paths=[filePath])


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


if __name__ == '__main__':
    main()
