# log
# v1.0
# Only Scripts
# v2.0
# promote into a plugin for cinema4d
#


####
importer_ext = [
    'c4d', 'abc', '3ds', 'dae', 'fbx', 'obj', 'stl', 'usda', 'usdc', 'ai'
]

exporter_plugin_id = {
    'c4d': 1001026,
    'abc': 1028082,
    '3ds': 1001038,
    'dae': 1025755,
    # 'obj': 1030178, # obj has error in python export
    'fbx': 1026370,
    'stl': 1001021,
    'usda': 1055179,
    'usdc': 1055179,
}

import c4d
from c4d import plugins, gui

import os


class PluginInfo():
    def get_import_plugin_id(self):
        d = dict()
        for p in c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_SCENELOADER, True):
            d[p.GetID()] = p.GetName()

    def get_export_plugin_id(self):
        d = dict()
        for p in c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_SCENESAVER, True):
            d[p.GetID()] = p.GetName()

    def get_plug_from_id(self, id, loader=False):
        op = dict()
        plug = plugins.FindPlugin(id, c4d.PLUGINTYPE_SCENESAVER if not loader else c4d.PLUGINTYPE_SCENELOADER)
        plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op)
        imexporter = op.get("imexporter", None)
        return imexporter


import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale

import subprocess


class Clipboard():
    def init_clipboard(self):
        self.file_urls = []

        self.CF_HDROP = 15

        u32 = ctypes.windll.user32
        k32 = ctypes.windll.kernel32
        s32 = ctypes.windll.shell32

        self.OpenClipboard = u32.OpenClipboard
        self.OpenClipboard.argtypes = w.HWND,
        self.OpenClipboard.restype = w.BOOL

        self.GetClipboardData = u32.GetClipboardData
        self.GetClipboardData.argtypes = w.UINT,
        self.GetClipboardData.restype = w.HANDLE

        self.SetClipboardData = u32.SetClipboardData

        self.CloseClipboard = u32.CloseClipboard
        self.CloseClipboard.argtypes = None
        self.CloseClipboard.restype = w.BOOL

        self.DragQueryFile = s32.DragQueryFile
        self.DragQueryFile.argtypes = [w.HANDLE, w.UINT, ctypes.c_void_p, w.UINT]

    def pull(self, force_unicode=False):
        self.init_clipboard()

        if self.OpenClipboard(None):
            h_hdrop = self.GetClipboardData(self.CF_HDROP)

            if h_hdrop:
                # expose force unicode to preferences(if enabled unicode beta setting)
                FS_ENCODING = getdefaultlocale()[1] if not force_unicode else 'utf-8'
                file_count = self.DragQueryFile(h_hdrop, -1, None, 0)

                for index in range(file_count):
                    buf = ctypes.c_buffer(260)
                    self.DragQueryFile(h_hdrop, index, buf, ctypes.sizeof(buf))
                    self.file_urls.append(buf.value.decode(FS_ENCODING))

        self.CloseClipboard()
        return self.file_urls

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


def get_config():
    import json

    directory, _ = os.path.split(__file__)
    config_path = os.path.join(directory, 'res', "config.json")

    with open(config_path, 'r') as f:
        config_data = json.load(f)
        FORCE_UNICORE = config_data.get('FORCE_UNICORE')
        TEMP_DIR = config_data.get('TEMP_DIR')
        return FORCE_UNICORE, TEMP_DIR


def report(msg, dialog=True):
    if dialog:
        c4d.gui.MessageDialog(msg)
    return print(msg)


class SuperImport(c4d.plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    dialog = None

    def Execute(self, doc):
        FORCE_UNICORE, TEMP_DIR = get_config()

        clipboard = Clipboard()
        file_list = clipboard.pull(force_unicode=FORCE_UNICORE)
        del clipboard  # release clipboard

        objs = [file for file in file_list if file.split('.')[-1] in importer_ext]

        for obj in objs[:]:
            try:
                c4d.documents.MergeDocument(doc, obj, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None)
            except Exception as e:
                print(e)

        c4d.EventAdd()

        return True


class SuperExport(c4d.plugins.CommandData):

    def Execute(self, doc):
        # pop up selection
        pos_x, pos_y = self.get_mouse_pos()
        index = self.popup_menu(int(pos_x), int(pos_y))
        if index < 0: return False  # not select

        # get selection ext
        ext_list = list(exporter_plugin_id)
        self.ext = ext_list[index]
        exporter_id = exporter_plugin_id.get(self.ext)

        # set path
        FORCE_UNICORE, TEMP_DIR = get_config()
        if TEMP_DIR == '':
            TEMP_DIR = os.path.join(os.path.expanduser('~'), 'spio_temp')
            if not "spio_temp" in os.listdir(os.path.expanduser('~')):
                os.makedirs(TEMP_DIR)

        filename = c4d.documents.GetActiveDocument().GetDocumentName()
        filePath = os.path.join(TEMP_DIR, filename + '.' + self.ext)

        self.set_export_scalue()
        sobj = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

        # seem that fbx not work with c4d.documents.IsolateObjects()
        if self.ext == 'fbx':
            self.check_fbx()
            if not c4d.documents.SaveDocument(doc, filePath, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, exporter_id):
                return report('Exporter Failed!')

            clipboard = Clipboard()
            clipboard.push_to_clipboard(paths=[filePath])
        else:
            try:
                tdoc = c4d.documents.IsolateObjects(doc, sobj)
                if not c4d.documents.SaveDocument(tdoc, filePath, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST,
                                                  exporter_id):
                    return report('Exporter Failed!')
                c4d.documents.KillDocument(tdoc)
                clipboard = Clipboard()
                clipboard.push_to_clipboard(paths=[filePath])
            except IndexError:
                report('Need to Selected Object!')
                return False

        return True

    def get_mouse_pos(self):
        state = c4d.BaseContainer()
        c4d.gui.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_MOUSELEFT, state)
        mx = state.GetReal(c4d.BFM_INPUT_X)
        my = state.GetReal(c4d.BFM_INPUT_Y)
        return mx, my

    def popup_menu(self, pos_x, pos_y):
        entries = c4d.BaseContainer()
        entries.SetString(0, "Super Export&d&")

        for i, (key, value) in enumerate(exporter_plugin_id.items()):
            entries.SetString(i + 2, key.upper())
        return c4d.gui.ShowPopupDialog(cd=None, bc=entries, x=pos_x, y=pos_y) - 2

    def set_export_scalue(self):
        unit_scale = c4d.UnitScaleData()
        unit_scale.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)

    def check_fbx(self):
        fbxExportId = 1026370
        plug = plugins.FindPlugin(fbxExportId, c4d.PLUGINTYPE_SCENESAVER)
        if plug is None:
            return report('Failed to retrieves Exporter!')
        # check exporter
        op = dict()

        if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
            return report('Failed to retrieves private data')

        fbxExport = op.get("imexporter", None)
        if fbxExport is None:
            return report('Exporter Not Found!')

        # set fbx exporter
        fbxExport[c4d.FBXEXPORT_ASCII] = False
        fbxExport[c4d.FBXEXPORT_SELECTION_ONLY] = True


#### Register

PLUGIN_ID_super_import = 1058794
PLUGIN_ID_super_export = 1058795


def register_icon():
    import os
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    icon_import = os.path.join(directory, "res", "import.tif")
    icon_export = os.path.join(directory, "res", "export.tif")

    bmp1 = c4d.bitmaps.BaseBitmap()
    bmp2 = c4d.bitmaps.BaseBitmap()
    # Init the BaseBitmap with the icon
    if bmp1.InitWith(icon_import)[0] != c4d.IMAGERESULT_OK: raise MemoryError("Failed to initialize the BaseBitmap.")
    if bmp2.InitWith(icon_export)[0] != c4d.IMAGERESULT_OK: raise MemoryError("Failed to initialize the BaseBitmap.")

    return bmp1, bmp2


if __name__ == '__main__':
    icon_import, icon_export = register_icon()
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID_super_import,
                                      str="Super Import",
                                      info=0,
                                      help="Copy Paste Import",
                                      dat=SuperImport(),
                                      icon=icon_import)

    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID_super_export,
                                      str="Super Export",
                                      info=0,
                                      help="Copy Paste Export",
                                      dat=SuperExport(),
                                      icon=icon_export)
