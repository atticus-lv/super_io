# log
# v0.1
# Only Scripts
# v0.2
# promote into a plugin for cinema4d


from __future__ import annotations

####
importer_ext = [
    'c4d', 'abc', '3ds', 'dae', 'fbx', 'obj', 'stl', 'usda', 'usdc', 'ai'
]
image_ext = [
    'jpg', 'png', 'jpeg', 'tif', 'tiff', 'tga', 'exr', 'hdr', 'psd'
]

# fix scale
importer_plugin_id = {
    'obj': 1030177,
    'stl': 1001020,
    'abc': 1028081,
}

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

import subprocess
import os
import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale


class Clipboard():
    def __init__(self, file_urls=None):
        if sys.platform not in {'win32', 'darwin'}:
            raise EnvironmentError

    def pull_files_from_clipboard(self, force_unicode):
        file_list = []

        if sys.platform == 'win32':
            clipboard = WinTypeClipboard()
            file_list = clipboard.pull(force_unicode)

            del clipboard

            if file_list is None:
                clipboard = PowerShellClipboard()
                file_list = clipboard.pull()

        elif sys.platform == 'darwin':
            clipboard = MacClipboard()
            file_list = clipboard.pull()

        return file_list

    def push_to_clipboard(self, paths):
        if sys.platform == 'win32':
            clipboard = PowerShellClipboard()
        elif sys.platform == 'darwin':
            clipboard = MacClipboard()

        clipboard.push_to_clipboard(paths)

    def push_pixel_to_clipboard(self, path):
        if sys.platform == 'win32':
            clipboard = PowerShellClipboard()
        elif sys.platform == 'darwin':
            clipboard = MacClipboard()

        clipboard.push_pixel_to_clipboard(path)


class MacClipboard():

    def pull(self, force_unicode=False):
        self.file_urls = []
        from .res import _native as pasteboard

        pb = pasteboard.Pasteboard()

        urls = pb.get_file_urls()

        if urls is not None:
            self.file_urls = list(urls)

        return self.file_urls

    def push_pixel_to_clipboard(self, path):
        commands = [
            "set the clipboard to "
            f'(read file POSIX file "{path}" as «class PNGf»)'
        ]

        subprocess.Popen(self.get_osascript_args(commands))

    def push_to_clipboard(self, paths):
        commands = [
            "set the clipboard to "
            f'(POSIX file "{paths[0]}")'
        ]

        subprocess.Popen(self.get_osascript_args(commands))

    def get_osascript_args(self, commands):
        args = ["osascript"]
        for command in commands:
            args += ["-e", command]
        return args


class PowerShellClipboard:
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

    def push_pixel_to_clipboard(self, path):
        script = (
            "Add-Type -Assembly System.Windows.Forms; "
            "Add-Type -Assembly System.Drawing; "
            f"$image = [Drawing.Image]::FromFile('{path}'); "
            "$imageStream = New-Object System.IO.MemoryStream; "
            "$image.Save($imageStream, [System.Drawing.Imaging.ImageFormat]::Png); "
            "$dataObj = New-Object System.Windows.Forms.DataObject('Bitmap', $image); "
            "$dataObj.SetData('PNG', $imageStream); "
            "[System.Windows.Forms.Clipboard]::SetDataObject($dataObj, $true); "
        )

        self.execute_powershell(script)

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

        self.execute_powershell(script)

    def pull(self):
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$files = Get-Clipboard -Format FileDropList; "
            "if ($files) { $files.fullname }"
        )

        popen, stdout, stderr = self.execute_powershell(script)

        self.file_urls = stdout.split('\n')
        self.file_urls[:] = [file for file in self.file_urls if file != '']

        return self.file_urls

    def execute_powershell(self, script):
        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
        popen = subprocess.Popen(**parms)
        stdout, stderr = popen.communicate()
        return popen, stdout, stderr


class WinTypeClipboard:
    def __init__(self):
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

    @property
    def file_list(self):
        return self.file_urls

    def pull(self, force_unicode=False):
        # get
        try:
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

            return self.file_urls
        except UnicodeError:
            pass
        finally:
            self.CloseClipboard()


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

    @staticmethod
    def get_plug_from_id(id, loader=False):
        op = dict()
        plug = plugins.FindPlugin(id, c4d.PLUGINTYPE_SCENESAVER if not loader else c4d.PLUGINTYPE_SCENELOADER)
        plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op)
        imexporter = op.get("imexporter", None)
        return imexporter


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


def import_image_as_plane(doc, image_path):
    img = image_path
    if not img:
        return 'Canvas Cancelled.'
    else:
        path, filename = os.path.split(img)
        # get filename
        fname, ext = filename.split('.')

        # create material
        mat = c4d.BaseMaterial(5703)
        mat[c4d.MATERIAL_USE_COLOR] = False
        mat[c4d.MATERIAL_USE_LUMINANCE] = True
        mat[c4d.MATERIAL_USE_ALPHA] = True
        mat[c4d.MATERIAL_USE_REFLECTION] = False
        mat[c4d.MATERIAL_PREVIEWSIZE] = + 12
        mat[c4d.MATERIAL_ANIMATEPREVIEW] = True

        doc.InsertMaterial(mat)
        ##add image to shader
        shdr_texture = c4d.BaseList2D(c4d.Xbitmap)
        shdr_texture[c4d.BITMAPSHADER_FILENAME] = img
        mat[c4d.MATERIAL_LUMINANCE_SHADER] = shdr_texture
        mat.InsertShader(shdr_texture)

        # create bitmap
        bm = c4d.bitmaps.BaseBitmap()
        bm.InitWith(img)
        getsize = bm.GetSize()
        x = getsize[0]
        y = getsize[1]

        ### check if image has alpha channel
        if bm.GetChannelCount() > 0:
            alpha_texture = c4d.BaseList2D(c4d.Xbitmap)
            alpha_texture[c4d.BITMAPSHADER_FILENAME] = img
            mat[c4d.MATERIAL_ALPHA_SHADER] = alpha_texture
            mat.InsertShader(alpha_texture)
            doc.AddUndo(c4d.UNDOTYPE_NEW, alpha_texture)

        ### create plane
        plane = c4d.BaseObject(5168)
        plane[c4d.PRIM_PLANE_SUBW] = 1
        plane[c4d.PRIM_PLANE_SUBH] = 1
        plane[c4d.PRIM_PLANE_WIDTH] = x
        plane[c4d.PRIM_PLANE_HEIGHT] = y
        doc.InsertObject(plane)
        ##assign texture tag to plane
        tag = plane.MakeTag(c4d.Ttexture)
        tag[c4d.TEXTURETAG_PROJECTION] = 6
        tag[c4d.TEXTURETAG_MATERIAL] = mat

        ## edit name
        mat[c4d.ID_BASELIST_NAME] = filename
        plane[c4d.ID_BASELIST_NAME] = fname


class SuperImport(c4d.plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    dialog = None

    def Execute(self, doc):
        FORCE_UNICORE, TEMP_DIR = get_config()

        clipboard = Clipboard()
        file_list = clipboard.pull_files_from_clipboard(force_unicode=FORCE_UNICORE)
        del clipboard  # release clipboard

        objs = [file for file in file_list if file.split('.')[-1] in importer_ext]
        images = [file for file in file_list if file.split('.')[-1] in image_ext]

        # import objects
        for obj in objs[:]:
            try:
                ext = obj.split('.')[-1]
                if ext in importer_plugin_id:
                    self.fix_scale(ext)
                c4d.documents.MergeDocument(doc, obj, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None)
            except Exception as e:
                print(e)

        # import images
        for img in images:
            import_image_as_plane(doc, img)

        c4d.EventAdd()

        return True

    def fix_scale(self, ext):
        id = importer_plugin_id.get(ext)
        imexporter = PluginInfo.get_plug_from_id(id, loader=True)

        unit_scale = c4d.UnitScaleData()
        unit_scale.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)

        if ext == 'obj':
            imexporter[c4d.OBJIMPORTOPTIONS_SCALE] = unit_scale
            imexporter[c4d.OBJIMPORTOPTIONS_NORMALS] = c4d.OBJIMPORTOPTIONS_NORMALS_VERTEX
            imexporter[c4d.OBJIMPORTOPTIONS_IMPORT_UVS] = c4d.OBJIMPORTOPTIONS_UV_ORIGINAL
            imexporter[c4d.OBJIMPORTOPTIONS_SPLITBY] = c4d.OBJIMPORTOPTIONS_SPLITBY_OBJECT
            imexporter[c4d.OBJIMPORTOPTIONS_MATERIAL] = c4d.OBJIMPORTOPTIONS_MATERIAL_MTLFILE

        elif ext == 'abc':
            imexporter[c4d.ABCIMPORT_SCALE] = unit_scale
        elif ext == 'stl':
            imexporter[c4d.STLIMPORTFILTER_SCALE] = unit_scale


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

        self.set_export_scale()
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

    def set_export_scale(self):
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
