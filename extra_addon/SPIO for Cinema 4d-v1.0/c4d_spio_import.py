# log
# v1.0 base importer finish

from __future__ import annotations

import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale

import c4d
from c4d import gui, plugins

# change it to 'True' if your system encode if utf-8 (win)
FORCE_UNICORE = False


def main():
    if sys.platform != "win32": return gui.MessageDialog("Not Support this platform!")

    clipboard = WintypesClipboard()
    file_list = clipboard.pull(force_unicode=FORCE_UNICORE)
    del clipboard  # release clipboard

    if len(file_list) == 0:
        return gui.MessageDialog('No files found!')

    op = {}
    plug = plugins.FindPlugin(1030177, c4d.PLUGINTYPE_SCENELOADER)

    if plug is None:
        return gui.MessageDialog('Importer Not Found!')

    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
        print(op)
        if "imexporter" not in op:
            return gui.MessageDialog('Importer Not Found!')

        objImport = op["imexporter"]
        if objImport is None:
            return gui.MessageDialog('Importer Not Found!')

        objs = [file for file in file_list if file.lower().endswith('.obj')]

        unit_scale = c4d.UnitScaleData()
        unit_scale.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)
        objImport[c4d.OBJIMPORTOPTIONS_SCALE] = unit_scale

        objImport[c4d.OBJIMPORTOPTIONS_NORMALS] = c4d.OBJIMPORTOPTIONS_NORMALS_VERTEX
        objImport[c4d.OBJIMPORTOPTIONS_IMPORT_UVS] = c4d.OBJIMPORTOPTIONS_UV_ORIGINAL
        objImport[c4d.OBJIMPORTOPTIONS_SPLITBY] = c4d.OBJIMPORTOPTIONS_SPLITBY_OBJECT
        objImport[c4d.OBJIMPORTOPTIONS_MATERIAL] = c4d.OBJIMPORTOPTIONS_MATERIAL_MTLFILE

        for obj in objs[:]:
            c4d.documents.MergeDocument(doc, obj, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None)


class WintypesClipboard():
    def __init__(self, file_urls=None):
        # file_urls: list[str] = None
        self.file_urls = file_urls

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
        self.file_urls = []

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


if __name__ == '__main__':
    main()
